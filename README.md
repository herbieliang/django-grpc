# Django gRpc 服务端
## 使用说明

- 下载或克隆本仓库

- 将  `django-grpc` 文件夹放入django项目的 `extra_apps` 目录中

- 修改settings.py文件，添加如下设置

  ```python
  import sys
  from extra_apps.django_grpc import utils as grpc_utils
  
  sys.path.insert(0, os.path.join(BASE_DIR, "extra_apps"))
  
  INSTALLED_APPS = [
      ...
      "extra_apps.django_grpc.apps.DjangoGrpcConfig",
  ]
  
  # gRpc settings
  GRPCSERVER = {
      "servicers": [
          
      ],  # register servicer function grpc_hook() here
      "interceptors": [
          
      ],  # optional, interceprots are similar to middleware in Django
      "maximum_concurrent_rpcs": None,
      "authentication": False,  # 认证方式，False为关闭认证，ssl为SSL/TLS证书认证
      "signature": False,
      "signature_data": {
          
      },
      "certificates": {
          "server_certificate": grpc_utils.load_credential_from_file(
              "credentials/localhost.crt"
          ),
          "server_certificate_key": grpc_utils.load_credential_from_file(
              "credentials/localhost.key"
          ),
          "root_certificate": grpc_utils.load_credential_from_file(
              "credentials/localhost.crt"
          ),
      },
  }
  ```

  - servicers：注册 grpc servicer 文件，每个文件应包含一个 grpc_hook() 方法，需要将此方法在这里注册
  - interceptors：grpc 拦截器，类似于 Django 的中间件，默认包含一个 `extra_apps.django_grpc.interceptors.SignatureValidationInterceptor`拦截器，用于校验 metadata 中是否包含 `signature_data` 中定义的键值对
  - maximum_concurrent_rpcs：最大连接数，为 `None` 时不限制
  - authentication：认证方式，`False` 为无须认证，`ssl` 为SSL/TLS证书认证，需要在 `certificates` 中配置证书信息，此项为 `False` 时 signature 认证设置无效
  - signature：是否开启附加认证，认证内容在 `signature_data` 中定义
  - signature_data：附加认证内容，键值对形式
  - certificates：SSL证书信息

- 定义 servicer，格式如下：

  ```python
  import helloworld_pb2
  import helloworld_pb2_grpc
  
  
  def grpc_hook(server):
      helloworld_pb2_grpc.add_GreeterServicer_to_server(
          HelloWorldServicer(), server
      )
  
  
  class HelloWorldServicer(helloworld_pb2_grpc.GreeterServicer):
      def SayHello(self, request, context):
          response = helloworld_pb2.HelloReply(message="Hello " + request.name)
          return response
  
  ```

  

## 启动 grpc 服务器

`python manage.py grpcserver`

附加参数：

- `—-max_workers` 最大进程数
- `--port` 端口号，默认50051