

import time
import selenium.webdriver
import subprocess as sp

def bigvid(driver, url, **kwargs):
    driver.get(url)
    
    # hop
    script = "document.getElementById('fplayer').contentWindow.start('download');"
    driver.execute_script( script )

    timeout = kwargs.get('timeout', 2)
    time.sleep(timeout)
    
    driver.switch_to_frame("fplayer")
    driver.switch_to_frame("stream")

    elem = driver.find_elements_by_css_selector('div.video_center a')[-1]

    link = elem.get_attribute('href')

    print 'found download link'
    return link, elem.text



def download( (url, filename) ):
    print 'downloading', url
    sp.check_call( ['aria2c',  '-m 0', '-c', '-x 1', '-o', filename, url] )


class Tubeplus:

    def __init__(self, driver):
        self.driver = driver


    def show(self, name):
        '''main page for tv show'''
        
        url = 'http://www.tubeplus.is/search/tv-shows/{}/'.format(name)
        self.driver.get(url)

        elem = self.driver.find_element_by_css_selector('a.plot')
        sub = elem.find_element_by_css_selector('b')

        return sub.text, elem.get_attribute('href')
        

    def seasons(self, url):
        self.driver.get(url) 

        seasons = self.driver.find_elements_by_css_selector('a.season')

        res = {}
        
        for s in seasons:
            res[int(s.text.split()[-1])] = s

        return res
    
    def episodes(self, s):
        s.click()
        time.sleep(1)
        
        data = self.driver.find_elements_by_css_selector('ul#links_list li.seasons a')

        return { int(d.text.split('-')[0].split()[-1]): d.get_attribute('href') for d in data }


    def link(self, url):
        self.driver.get(url)

        elems = self.driver.find_elements_by_class_name('link')

        for e in elems:
            a = e.find_element_by_tag_name('a')
            if 'bigvid.me' in a.get_attribute('href'):
                url = a.get_attribute('onclick').split("'")[1]
                break

        return 'http://bigvid.me/{0}'.format(url)
        
import argparse

parser = argparse.ArgumentParser(description = 'get stuff online.')

parser.add_argument('--title', '-t', type = str, help='name of the show', required = True)
parser.add_argument('--season', '-s', type = int, help='season', required = True)
parser.add_argument('--episode', '-e', type = int, help='episode', required = True)
parser.add_argument('--retry', '-r', type = int, help='retry', default = 5)

args = parser.parse_args()


driver = selenium.webdriver.PhantomJS()

print 'selenium/phantomjs started'

agent = Tubeplus(driver)


show, url = agent.show( args.title )

print 'found match:', show

seasons = agent.seasons(url)
episodes = agent.episodes(seasons[ args.season ])
link = agent.link(episodes[ args.episode ])

print 'found link:', link

for i in xrange(args.retry):
    info = bigvid(driver, link)

    try:
        download( info )
        break
    except sp.CalledProcessError:
        print 'download error, retrying with a new link'
        
driver.quit()
