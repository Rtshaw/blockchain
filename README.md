# 用Python從零開始創建區塊鏈

本文是博客：[用Python从零开始创建区块链](http://learnblockchain.cn/2017/10/27/build_blockchain_by_python/) 的原始碼. 
翻譯自[Building a Blockchain](https://medium.com/p/117428612f46)

[博客地址](http://learnblockchain.cn/2017/10/27/build_blockchain_by_python/)| [英文README](https://github.com/xilibi2003/blockchain/blob/master/README-en.md) 

## 安裝

1. 安裝 [Python 3.6+](https://www.python.org/downloads/) is installed. 
2. 安裝 [pipenv](https://github.com/kennethreitz/pipenv). 

```
$ pip install pipenv 
```

3. 創立一個 virtual env. 

```
$ pipenv --python=python3.6
```

4. 安裝依賴.  

```
$ pipenv install 
``` 

5. 運行節點:
    * `$ pipenv run python blockchain.py` 
    * `$ pipenv run python blockchain.py -p 5001`
    * `$ pipenv run python blockchain.py --port 5002`
    
## Docker運行

另一種方式是使用Docker運行：

1. clone repo
2. 建立docker容器

```
$ docker build -t blockchain .
```

3. 運行

```
$ docker run --rm -p 80:5000 blockchain
```

4. 添加多個節點:

```
$ docker run --rm -p 81:5000 blockchain
$ docker run --rm -p 82:5000 blockchain
$ docker run --rm -p 83:5000 blockchain
```

## 貢獻
[深入浅出区块链](http://learnblockchain.cn/) 想做好的區塊鏈學習博客。
[博客地址](https://github.com/xilibi2003/learnblockchain) 歡迎大家一起參預貢獻，一起推動區塊鏈技術發展。




