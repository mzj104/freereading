# Freereading
******
## 1. 项目背景
API正确性是Paddle质量的基石，影响业务训练、推理，影响用户对Paddle的信赖。至关重要。为保障Paddle API正确性，我们开发了PaddleAPITest。

目前主要考虑的正确性问题有**3**类：
>1）API**精度**正确性；
>
>2）一些**特大**Tensor，尤其是numel超过int32上限的Tensor计算异常；
>
>3）**0-Size**（numel为0的Tensor） Tensor不支持。

PaddleAPITest主要工作思路如下：
1. 在Paddle开发Trace API机制，具体见 https://github.com/PaddlePaddle/Paddle/pull/70752 ，用于抓取API调用配置，下面是一个配置例子：
```
paddle.concat(tuple(Tensor([31376, 768],"float32"),Tensor([1, 768],"float32"),), axis=0, )
```
2. 在所有Paddle单元测试（CI）、集成测试（CE）流水线中，抓取所有Paddle API的调用配置，形成了PaddleAPITest/tester/api_config下以“api_config_CI”，“api_config_CE”开头的配置集。对以上配置集进行去重、排序、梳理得到了以“api_config_merged”开头的配置集。

3. 在 PaddleAPITest 中开发一套**引擎**，加载配置集，初始化相应Tensor，调用相应API执行前/反向测试。

4. 在 PaddleAPITest 中开发一套**转换工具**，在调用Paddle API测试的同时，等同的调用Torch API，做精度对比测试。

5. 对采集到的配置集进行shape篡改，得到了“bigtensor”、“0sizetensor”开头的配置集。

6. 通过与Torch对比，如果出现以下情况则认为Paddle API有必要确认是否正确并修复：
>a. 精度diff
>
>b. Torch正常，Paddle报错
>
>c. Torch正常，Paddle **CoreDump**或**CUDA Error**



