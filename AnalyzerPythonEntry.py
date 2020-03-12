# -*- coding: utf-8 -*-
"""
    @Author  : Ray820328@163.com
    @Time    : 2020/03/02
    @Comment : 
"""
import sys
import os,shutil
import os.path
from xml.dom.minidom import parse
sys.path.append("./Python/Utils/")
sys.path.append("./Python/Logic/")
import FileUtil
import XmlUtil
import ConfigManager
import ProjectManager
import GitManager
import BuildLogManager
import MailManager

def showHelp():
    print("Parameters as:\n\
            1 - config file location(json)\n\
            2 - opration type[0|1|2]\n\
                [0] - update the VS project file from the dll files\n\
                [1] - export references and dlls from the VS project file\n\
                [2] - pull the latest codes and build\n\
        ")

if __name__ == '__main__':
    configPath = sys.argv[1]
    #print(sys.path)
    if configPath.startswith("./"):
        configPath = os.path.join(FileUtil.getEntryFilePath(), configPath[2:])
    elif ":" in configPath or configPath.startswith("/"):
        print("configPath = %s" % (configPath))
    else:
        configPath = os.path.join(sys.path[1], configPath)

    try:
        jsonDict = ConfigManager.loadConfig(configPath)
        ConfigManager.setGlobalConfig(jsonDict)

        filePath = ConfigManager.getValue(ConfigManager.key_project_file_path)
        domTree, rootNode = XmlUtil.readXML(filePath)
        destDllDir = "./TempDir"

        localDir = ConfigManager.getValue(ConfigManager.key_project_local_dir)
        repoType = ConfigManager.getValue(ConfigManager.key_project_repository_type) #目前仅支持git
        repoRemote = ConfigManager.getValue(ConfigManager.key_project_repository_address)
        branchName = ConfigManager.getValue(ConfigManager.key_project_branch_name)
        buildLogFile = ConfigManager.getValue(ConfigManager.key_project_build_log_file)
        reportLevels = ConfigManager.getValue(ConfigManager.key_project_report_level)
        reportKeys = ConfigManager.getValue(ConfigManager.key_project_report_keys)
    except:
        showHelp()
        exit(0)

    if rootNode == None:
        print("xml文件错误")
        showHelp()
        exit(0)
    elif len(sys.argv) >= 3 and sys.argv[2] == '0':
        #更新工程文件，除非工程引用或库有改动，否则不执行
        ProjectManager.updateProjectXml(domTree, rootNode, filePath, destDllDir)
    elif len(sys.argv) >= 3 and sys.argv[2] == '1':
        #导出dll等引用，除非工程dll有改变，否则可以不执行
        ProjectManager.exportProjectReferences(rootNode, destDllDir)
    elif len(sys.argv) >= 3 and sys.argv[2] == '2':
        #更新工程
        GitManager.pullProject(localDir, repoRemote, branchName)

        timeFrom = "2.month.ago"
        timeTo = "" # --until=1.day.ago
        changeInfoDic = GitManager.getLogsFromProject(localDir, timeFrom, timeTo)
        for key, value in changeInfoDic.items():
           print(key + ' -> ' + value)

        #构建工程
        projectFilePath = ProjectManager.getProjectFilePath(filePath)
        print("\n\n###Start to build project, dest = %s" % (projectFilePath))
        dirPath, projectFileName = os.path.split(projectFilePath)
        buildLogLines = ProjectManager.buildProject(projectFileName, buildLogFile)

        #分析编译日志，发邮件
        reportLogLines = BuildLogManager.filterContent(buildLogLines, reportLevels, reportKeys)
        MailManager.sendEmailByLogs(changeInfoDic, reportLogLines)
    else:
        showHelp()
