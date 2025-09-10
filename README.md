
<div align="center">
<a href="https://demo.ragflow.io/">
<img src="https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/logo3.png" width="150" alt="zyznt logo">
</a>
</div>

<h2 align="center">卓越智能体zyznt</h2></br> </br></br>



*卓越智能体*
</br> </br>
zyznt 是一个开源的 LLM 企业级应用开发平台。其直观的界面结合了 Agent、RAG 管道、AI 工作流、模型管理、智能数据BI、智能客服等，让您可以快速从需求到应用。以下是其核心功能：
</br> </br>

![zyznt-v1](https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/zyznt.png)
</br> </br>
**1. Agent 智能体**:
您可以基于 LLM模型、提示词、RAG知识库、MCP服务、BI数据源、BI数据模型等定义专属的企业级智能体，并为智能体添加预构建或自定义工具。zyznt 为 AI Agent 提供了多种内置工具、智能体MCP服务封装、智能数据BI、智能客服等功能。

**2. RAG 智能知识库**:
智能的知识增强功能，涵盖从文档解析录入到检索的所有功能，支持从 Word、PDF、PPT、 Excel、TXT等其他常见文档格式中提取文本的开箱即用的支持。

**3. AI工作流**:
可视化工作流编排，在画布上构建和测试功能强大的 AI 工作流程，利用LLM模型、条件判断、数据处理、MCP工具、自定义代码、api、数据源连接、数据可视化、TEXT2SQL、RAG、智能体等组件，构建您专属的企业级AI工作流。

**4. 智能数据BI**:
平台拥有数据源连接、数据模型、数据可视化模块，结合智能体、RAG、AI工作流，打造全新智能的数据BI服务，实现智能问数（ChatBi）、业务需求一键转为数据可视化模型、智能数据监控、结合AI工作流实现复杂数据融合展示、智能归因分析、智能数据挖掘等数据分析功能。

**5. API开放**:
zyznt 的所有功能都带有相应的 API，因此您可以轻松地将 zyznt 集成到自己的业务逻辑中。
</br> </br>

## 使用 zyznt

- **zyznt云平台 http://ai.zyznt.com </br>**
  我们提供[ zyznt 云服务](http://ai.zyznt.com)，任何人都可以注册使用。它提供了自部署版本的所有功能，让您快速体验和使用zyznt的全面功能。</br></br>

- **zyznt 社区版</br>**
  使用以下部署方式快速在您的环境中运行 zyznt。</br></br>


- **面向企业的 zyznt 商业版</br>**
  我们提供额外的面向企业的功能。[给我们发送电子邮件zyun@zy-yun.com或加以下微信](zyun@zy-yun.com)沟通您的企业需求。 </br></br>



## 安装社区版

### 系统要求

在安装 zyznt 之前，请确保您的机器满足以下最低系统要求：

- CPU >= 2 Core
- RAM >= 4 GiB

### 快速部署和启动

启动 zyznt 服务的最简单方法是运行我们的 [docker-compose.yml](zyznt-docker/docker-compose.yml) 文件。在运行安装命令之前，请确保您的机器上安装了 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)：

```bash
git clone https://dws9088:a3b949bf8237f9558ca23c0c66ff7f27@gitee.com/dws9088/zyzntai.git .
cd zyznt-docker
docker-compose up -d
```

服务启动后，可以在浏览器上访问 [http://localhost:80](http://localhost:80) 登录 zyznt 管理员后台，默认的用户名和密码为 `admin@zyznt` 和 `zyzntai`。

### 自定义配置

如果您需要自定义配置，可以修改zyznt-docker目录中file文件夹内的配置文件，[conf.txt](zyznt-docker/file/conf.txt)是后端服务配置文件，[env.production](zyznt-docker/file/env.production)是编译前端项目用的配置文件，[zyzntweb.conf](zyznt-docker/file/zyzntweb.conf)是nginx配置文件。</br></br></br></br>


## 👥 加入社区

扫二维码添加 zyznt 助手，进 zyznt 社区交流群。</br></br>

<p align="center">
  <img src="https://zy-wendang.oss-cn-hangzhou.aliyuncs.com/img/weixin-zyznt.png" width=20% height=30%>
</p>

</br></br>


## License

本仓库遵循 [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) 开源协议。













