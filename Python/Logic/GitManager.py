# -*- coding: utf-8 -*-
"""
    @Author  : Ray820328@163.com
    @Time    : 2017/03/05
    @Comment : 
"""
import os
import sys
import git
from git import Repo
from git import RemoteProgress
import StringUtil

def pullProject(localDir, gitRemote, branchName):
    gitPath = os.path.join(localDir, ".git")
    if (not os.path.isdir(gitPath)):
        print("----------init new repo")
        #repo = Repo.init(gitPath, bare=True)

        repo = Repo.clone_from(gitRemote, localDir) # , branch='master'
    else:
        print("----------load repo")
        repo = Repo(localDir)

    try:
        remote = repo.remote()
        origin = remote
        print("Remote origin is exists.")
    except:
        print("Remote origin is empty,creating..")
        origin = repo.create_remote('origin', gitRemote)
     
    remote = repo.remote()   
    #remote.fetch()
    remote.pull()

    #切换分支
    try:
        #a、本地存在此分支
        repo.refs[branchName]
        repo.head.reference = repo.heads[branchName]
        repo.heads[branchName].set_tracking_branch(remote.refs[branchName]).checkout()
        print("Exist local branch = %s" % (branchName))
    except:
        #b、本地不存在，需要从远程拉取
        print("Not exist local branch = %s" % (branchName))
        repo.create_head(branchName, remote.refs[branchName]).set_tracking_branch(remote.refs[branchName]).checkout()
        print("Branch created, name = %s" % (branchName))
    
    try:
        origin = repo.remotes['origin']
        assert origin.exists()
        #assert not repo.delete_remote(origin).exists()
        origin.pull()
    except:
        print("*** Git Update project failed.")
        assert False

    #git command
    #git = repo.git
    #git.checkout('HEAD', b=xxx)

    print("----------pull from remote repo finished.")

def getLogsFromProject(localDir, timeFrom, timeTo):
    #repo = git.Repo.clone_from(self._small_repo_url(), os.path.join(rw_dir, "repo"), branch="master")
    repo = Repo(localDir)
    assert not repo.bare # 版本库是否为空版本库
    heads = repo.heads
    master = heads.master       # lists can be accessed by name for convenience
    #master.commit
    
    g = git.Git(localDir) 
    # "--pretty=tformat:" raw "--numstat" --author="John\|Mary”，Marry和John git log -- *.cs bar.py 文件名应该放到参数的最后位置
    #--grep="JRA-224" 可以传入-i用来忽略大小写, 同时使用--grep和--author，必须加一个--all-match参数
    keyDate = "Date "
    keyAuthor = "Author "
    keyAuthorLen = len(keyAuthor)
    log = g.log("--since=" + timeFrom, "--no-merges", "--oneline", "--pretty=tformat:" + keyDate + "%ci\n" + keyAuthor + "%ce", "--name-status", "*.cs")
    logList = log.split("\n")
    #print("----------")
    #print(log)
    
    changeInfoDic = {}
    authorEmail = ""
    for logLine in logList:
        logLine = logLine.strip()
        if logLine == "":
            continue
        #logLine = logLine.expandtabs()
        contents = logLine.split('\t')
        contentLen = len(contents)
        if contentLen > 1:
            modifiedFilePath = contents[contentLen - 1]
            #print("%s" % (modifiedFilePath))
            changeInfoDic[modifiedFilePath] = authorEmail
        elif logLine.startswith(keyAuthor):
            authorEmail = logLine[keyAuthorLen:]
            if not StringUtil.isEmail(authorEmail):
                print("Invalid email address: %s" % (authorEmail))
                #assert False
        else:
            contents = logLine.split(' ')
            #if logLine.find('M') == 0:
            #print("%i===%s" % (len(contents), logLine))
    
    return changeInfoDic

if __name__ == "__main__":
    sys.path.append("../../Python/Utils/")
    import StringUtil

    localDir = "D:/workspace/xxx" #
    gitRemote = "https://gitlab.xxx.git"
    pullProject(localDir, gitRemote)

    timeFrom = "1.month.ago"
    timeTo = "" # --until=1.day.ago
    changeInfoDic = getLogsFromProject(localDir, timeFrom, timeTo)
    for key, value in changeInfoDic.items():
       print(key + ' -> ' + value)
