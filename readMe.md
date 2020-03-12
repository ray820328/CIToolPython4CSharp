# C#编码规范检测集成工具（Mac）

- Author：易锐 <Ray820328@163.com>
- Date：2018/03/05

---

## 简介
  按项目需求，对目标C#项目或文件目录进行自定义代码规范检测，系统有以下特点：
- 自定义规则，可在规则源码工程实现任意要求的规则。（基于Rosly编译器）
- 同时支持服务器运行和IDE，跨平台运行，同时易于集成到CI系统。（本文介绍服务器运行环境和开发流程）
- 集成了基本的远程仓库版本管理操作到脚本系统，适合团队在线开发。（目前集成了git）
- 集成了邮件系统，以配置和模板的方式简化操作。
- 分析和报告采用纯Python实现，无shell等其他脚本文件，便于维护和升级。

## 安装基础组件
### 安装ssl

  ``` shell
  brew install openssl
  ```

### 安装 .Net Core
- 下载pkg安装
  - https://dotnet.microsoft.com/learn/dotnet/hello-world-tutorial/install

- 安装mono环境
  - 下载pkg并安装
    https://www.mono-project.com/download/stable/
  - 设置环境变量
    ``` shell
    vi ~/.bash_profile
    export PATH=/Library/Frameworks/Mono.framework/Versions/Current/Commands:${PATH}
    ```

### 安装Git环境
 - 略

### 安装Python环境
 - 版本Python 3.7.6
 - 安装gitpython
  ``` shell
  sudo pip install gitpython
  ```

## 工程与编码
### 自定义规则编码实现
- 打开StyleCopAnalyzers工程
  按以下流程实现自定义规则
- 新建自定义规则文件，如: SA1502ElementMustNotBeOnASingleLine
  - 定义自定义规则ID
  ``` C#
  public const string DiagnosticId = "SA1502";
  ```

  - 实现自定义规则
  ``` C#
  private static void CheckViolation(SyntaxNodeAnalysisContext context)
  {
      var openingBraceLineSpan = openBraceToken.GetLineSpan();
      var closingSpan = closeBraceToken.GetLineSpan();

      if (openingBraceLineSpan.EndLinePosition.Line == closingSpan.StartLinePosition.Line)
      {
          context.ReportDiagnostic(Diagnostic.Create(Descriptor, openBraceToken.GetLocation()));
      }
  }
  ```

  - 注册自定义规则检测
  ``` C#
  public override void Initialize(AnalysisContext context)
  {
      context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
      context.EnableConcurrentExecution();

      context.Register(BaseTypeDeclarationAction, SyntaxKinds.BaseTypeDeclaration);
      context.Register(BasePropertyDeclarationAction, SyntaxKinds.BasePropertyDeclaration);
  }
  ```

- 打包StyleCopAnalyzers工程
  StyleCopAnalyzers.dll

### 为项目添加检测环境
- 在项目代码工程根目录下新建文件夹 'CodeAnalyzer'（以下简称Analyzers工程目录）
- 拷贝工程文件Assembly-CSharp.csproj，导入StyleCop.Analyzers环境
  ``` shell
  dotnet add Assembly-CSharp.csproj package StyleCop.Analyzers --version 1.1.118
  ```
- 拷贝自制的模板工程文件CodeAnalyzerTemplate.csproj到Analyzers工程目录
  ``` xml
  <PropertyGroup>
    <CodeAnalysisRuleSet>MyStyleCopAnalyzer.ruleset</CodeAnalysisRuleSet>
  </PropertyGroup>

  <PropertyGroup>
    <DefineConstants>DEBUG;UNITY_EDITOR</DefineConstants>
    <NoWarn>0169</NoWarn>
    <AllowUnsafeBlocks>True</AllowUnsafeBlocks>
  </PropertyGroup>
  <PropertyGroup>
    <EnableDefaultNoneItems>false</EnableDefaultNoneItems>
  </PropertyGroup>
  <PropertyGroup>
    <EnableDefaultItems>false</EnableDefaultItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="../Assets/XXX/**/*.cs" />
  </ItemGroup>
  ```
- 拷贝自定义StyleCop.Analyzers配置文件到Analyzers工程目录
  stylecop.json
  ``` json
  {
    ...
    "settings": {
      "indentation": {
        "indentationSize": 4,
        "useTabs": false, 
      },
      "namingRules": {
        "includeInferredTupleElementNames": true,
        "tupleElementNameCasing" : "camelCase",
      "allowedNamespaceComponents": [
          "XXX_",
        ],
      "allowedHungarianPrefixes": [
          "XXX_",
        ]
      },
    ...
  }
  ```
- 拷贝规则配置文件到Analyzers工程目录
  MyStyleCopAnalyzer.ruleset
  ``` xml
  <RuleSet Name="Sample rule set" Description="" ToolsVersion="14.0">
    <Rules AnalyzerId="StyleCop.Analyzers" RuleNamespace="StyleCop.Analyzers">
      <Rule Id="SA1027" Action="None" /> <!-- 错误使用Tab和空格键，禁止Tab缩进 -->
      <Rule Id="SA1101" Action="None" /> <!-- 访问成员变量或方法需要带 'this.' 前缀 -->
      <Rule Id="SA1412" Action="Warning" /> 
      ...
    </Rules>
  </RuleSet>
  ```
- 拷贝库文件到Analyzers工程目录
  TempDir整个目录

### 更新库文件应用自定义规则
- 将目标库文件替换为StyleCopAnalyzers工程打包的dll
  ``` shell
  cp StyleCop.Analyzers.dll /Users/Ray/.nuget/packages/stylecop.analyzers/1.1.118/analyzers/dotnet/cs
  ```

## 脚本与分析报告
### 脚本工程操作
- 拷贝Python工程到Analyzers工程目录
- Python入口AnalyzerPythonEntry.py
- 脚本配置文件模板 【Python/Config.json】
  ``` json
  {
    "project" : {
      "localDir" : "",
      "repositoryType" : "git",
        "repositoryAddress" : "",
        "branchName" : "xxx_build",
        "buildLogFile" : "Build.log",
        "reportLevels" : ["warning"],
        "reportKeys" : ["SA"],
      "filePath" : "./CodeAnalyzerTemplate.csproj"
    },
    "memberEmails" : {
      "xxx@xxx.com" : ["xxx"]
    },
    "adminEmails" : {
      "0" : []
    },
    "emailServerConfig" : {
      "ip" : "xxx",
      "port" : "465",
      "account" : "xxx",
      "password" : "xxx",
      "emailSender" : "xxx",
      "tls" : "True"
    },
    "emailData" : {
      "title" : "编码规范检测报告",
      "body" : "编码规范检测信息:<br/><br/><br/>"
    },
    "none" : "none"
  }
  ```

### 执行脚本
- 拉取远程库工程源码进行检测，并提交报告到配置的目标邮箱
  ``` shell
  python AnalyzerPythonEntry.py ./Python/Config.json 2
  ```

- 更新Assembly-CSharp.proj文件【仅在dll有新增时执行】
  ``` shell
  python AnalyzerPythonEntry.py ./Python/Config.json 0
  ```

- 导出dll，此处Assembly-CSharp为VS生成的工程文件，默认生成TempDir（仅在dll有更新时需要执行，需要Unity和VS环境）
  ``` shell
  python AnalyzerPythonEntry.py ./Python/Config.json 1
  ```

## 生产环境
### CI集成或自定义运行
  略

## 其他
### 编码强制忽略某些检测规则
``` C#
  [ExcludeFromCodeCoverage]
  [SuppressMessage("StyleCop.CSharp.DocumentationRules", "SA1623:Property summary documentation should match accessors.", Justification = "This property behaves more like an opaque value than a Boolean.")]
```

## 参考
- https://github.com/microsoft/msbuild/blob/master/documentation/wiki/Building-Testing-and-Debugging-on-.Net-Core-MSBuild.md
- https://forum.unity.com/threads/unity-and-stylecop-analyzers.639784/
- 规则配置说明
  - https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/documentation/Configuration.md
  - https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/StyleCop.Analyzers/StyleCop.Analyzers.ruleset
