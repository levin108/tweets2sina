#!/usr/bin/env python
#encoding:UTF-8

import oauthapi
import simplejson
import time
import sys, os
from oauthUpdate import Sina
from weibopy.error import WeibopError
import re
import cfg

def daemonize(stdout='/dev/null', stderr=None, stdin='/dev/null',  
              pidfile=None, startmsg = 'started with pid %s' ):  
    cwd = os.getcwd()
    # flush io  
    sys.stdout.flush()  
    sys.stderr.flush()  
    # Do first fork.  
    try:  
        pid = os.fork()  
        if pid > 0: sys.exit(0) # Exit first parent.  
    except OSError, e:  
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))  
        sys.exit(1)         
    # Decouple from parent environment.  
    os.chdir("/")  
    os.umask(0)  
    os.setsid()  
    # Do second fork.  
    try:  
        pid = os.fork() 
        if pid > 0: sys.exit(0) # Exit second parent.  
    except OSError, e:  
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))  
        sys.exit(1)  
    # Open file descriptors and print start message  
    if not stderr:
        stderr = stdout  
        si = file(stdin, 'r')  
        so = file(stdout, 'a+')  
        se = file(stderr, 'a+', 0)  #unbuffered  
        pid = str(os.getpid())  
        sys.stderr.write("\n%s\n" % startmsg % pid)  
        sys.stderr.flush()  
    if pidfile:
        file(pidfile,'w+').write("%s\n" % pid)  
        # Redirect standard file descriptors.  
        os.dup2(si.fileno(), sys.stdin.fileno())  
        os.dup2(so.fileno(), sys.stdout.fileno())  
        os.dup2(se.fileno(), sys.stderr.fileno())  
    while True:
        main()
        time.sleep(2 * 60)

def savemaxid(maxid):
    f = open('%s/max.dat' % cfg.log_directory, 'w')
    f.write('%ld' % maxid)
    f.close()

def getmaxid():
    try:
        f = open('%s/max.dat' % cfg.log_directory, 'r')
        maxid = long(f.read())
        f.close()
    except:
        maxid = long(0)
    return maxid

def writelog(message):
    f = open('%s/log.txt' % cfg.log_directory, 'a+')
    f.write(message + '\n')
    f.close()

def main():
    if len(cfg.http_proxy_host) == 0 or len(cfg.http_proxy_port) == 0:
        client = oauthapi.tpOAuth()
    else:
        client = oauthapi.tpOAuth(http_proxy = {
            'host': cfg.http_proxy_host,
            'port': cfg.http_proxy_port
            })

    maxid = getmaxid()

    try:
        response = client.fetch_user_timeline(cfg.screen_name, 0, maxid + 1, 1, cfg.sync_rt_message)
        tweets = simplejson.loads(response)
    except:
        writelog('Twitter API limited')
        print 'API limited'
        return

    if maxid == 0:
        writelog('now tweets max id is %s' % tweets[0]['id'])
        savemaxid(tweets[0]['id'])
        return

    sina = Sina()
    sina.setToken(cfg.sina_access_token_key, cfg.sina_access_token_secret)
    #sina.update('hello sina microblog, abcd, F**K the developers of the API')
    for tweet in tweets:
        if maxid <= long(tweet['id']):
            maxid = long(tweet['id'])
        if not cfg.sync_reply_message and tweet['in_reply_to_user_id']:
            continue
        try:
            retweet = tweet['retweeted_status']
            text = retweet['text']
            mentions = retweet['entities']['user_mentions']
            for mention in mentions:
                p = re.compile('@' + mention['screen_name'])
                text = p.sub(mention['screen_name'], text)
            text = u"转:" + text
        except Exception, e:
            text = tweet['text']
            mentions = tweet['entities']['user_mentions']
            for mention in mentions:
                p = re.compile('@' + mention['screen_name'])
                text = p.sub(mention['screen_name'], text)
        try:
            msg = "update---: " + text
            writelog(msg.encode('utf8'))
            sina.update(text)
        except WeibopError as e:
            writelog('sina error, maybe api limited')

        writelog('now tweets max id is %ld' % maxid)
        savemaxid(maxid)

        time.sleep(120)

if __name__ == "__main__":
    daemonize()
