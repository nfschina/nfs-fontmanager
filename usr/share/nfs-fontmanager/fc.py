#-*- encoding:utf-8 -*-
u'''
@author: guoliang@nfschina.com
'''

from __future__ import absolute_import
import pandas as pd
import os
import sys
from pathlib import Path
import glsu

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

def installFonts(files):
    res = glsu.checkSudo()
    if res:
        dest = u'/usr/local/share/fonts/'
    else: 
        os.system(u'mkdir -p ~/.local/share/fonts/')
        dest = u'~/.local/share/fonts/'   
    try:
        for file in files:
            cmd = u'cp %s %s' % (file, dest) 
            res = glsu.run(cmd)
            if res != 0:
                return res, cmd
        #-i before cd because cd can't be run directly in sudo
        #glsu.run(['mkfontscale', 'mkfontdir', 'fc-cache -fv'])
        cmd = [u'mkfontscale', u'mkfontdir', u'fc-cache -fv', u'rm -f fontsdir', u'rm -f fonts.scale']
        res = glsu.run(cmd)
        return res, cmd        
    except Exception, e:
        return e, cmd
    
def installFontFiles(files):
    res = glsu.checkSudo()
    if res:
        dest = u'/usr/local/share/fonts/'
    else: 
        os.system(u'mkdir -p ~/.local/share/fonts/')
        dest = u'~/.local/share/fonts/'   
    try:
        cmd = u'cp %s %s' % (files, dest) 
        res = glsu.run(cmd)
        if res != 0:
            return res, cmd
        #-i before cd because cd can't be run directly in sudo
        #glsu.run(['mkfontscale', 'mkfontdir', 'fc-cache -fv'])
        cmd = [u'mkfontscale', u'mkfontdir', u'fc-cache -fv', u'rm -f fontsdir', u'rm -f fonts.scale']
        res = glsu.run(cmd)
        return res, cmd        
    except Exception, e:
        return e, cmd

def uninstallFonts(files):
    try:
        for file in files:
            cmd = u'rm %s' % file
            user_home = os.path.expanduser('~')
            dest = user_home+'/.local/share/fonts/'
            #TY_os uninstall system fonts need use 'gksu' 
            if os.path.exists("/etc/.systeminfo") or file.startswith(dest) :
                res = glsu.run(u'rm %s' % file)
            else:
                res = glsu.run(u'gksu rm %s' % file)
            if res!=0:
                return res, cmd
        cmd = u'fc-cache -fv'
        res = glsu.run(cmd)
        return res, cmd
    except Exception, e:
        return e, cmd

     
def listFc():
    outputs = os.popen(u'fc-list -v').read()
    parts = outputs.split(u'\n\n')
    df = None
    for part in parts:
        font = {}
        if part.strip() == u'':
            continue
        try:
            up = part.split(u'\tindex:')[0]
#            font[u'charset'] = part.split(u'\tcharset:')[1].split(u'\n(s)\n')[0]
#            down = part.split(u'\tcharset:')[1].split(u'\n(s)\n')[1]
        except Exception, e:
            print u'{}'.format(e)
            sys.exit(0)
#        updown = up+down
#        lines = updown.split(u'\n')[1:]
        lines = up.split(u'\n')[1:]
        for line in lines:
            words = line.split(u':')
            key = words[0].strip()
            if( key != 'family' and key != 'style' and key != 'fullname' and key != 'file') :
                continue
            value = u':'.join(words[1:])
            value = value.strip()
            if value.endswith(u'(s)'): value = value[:-3]
            if value.endswith(u'(i)'): value = value[:-3]
            if value.startswith(u'"') and value.endswith(u'"'): value = value[1:-1]
            value = value.strip()
            #print(key, value)
            font[key] = [value]
        if u'family' in font:
            font[u'family_'] = font[u'family'][0].split(u'"')[0]
        else:
            font[u'family_'] = u'font without family!'
        if u'style' in font:
            font[u'style_'] = font[u'style'][0].split(u'"')[0]
        else:
            font[u'style_'] = u'font without style!'
        if u'fullname' in font:
            font[u'fullname_'] = font[u'fullname'][0].split(u'"')[0]
        else:
            font[u'fullname_'] = u'font without fullname'
        #is symbol link?
        font[u'is_symlink_'] = Path(unicode(font[u'file'][0]).encode('utf-8')).is_symlink()
        font[u'file'] = font[u'file'][0] if not font[u'file'][0].startswith(u'/usr/share/fonts/truetype/') else font[u'file'][0][len(u'/usr/share/fonts/truetype/'):]
        df_font = pd.DataFrame.from_dict(font)
        if df is None:
            df = df_font
        else:
            df = pd.concat([df, df_font])
            #df = pd.concat([df, df_font],sort=False)
    df = df.reset_index()        
    return df

if __name__ == u'__main__':
    df = listFc()
#    print(df[['family_', 'style', 'fullname', 'file']])
#    print(df[['family_', 'style_', 'fullname_', 'file']])
    df.to_csv(u'fonts.csv')

        
