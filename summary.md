**commit** 是节点

**分支** 是指向节点的指针(   一个哈希值 )

**HEAd 指向分支**

commit时  Head指向的分支  会指向最新节点



![image-20261103153642935](C:\Users\mshx\AppData\Roaming\Typora\typora-user-images\image-20261103153642935.png)



**merge 时**  主要看 文件的位置 以及 对应行数是否有冲突  先找到最近的公共祖先 再进行合并



**绑定到远程仓库  并在远程仓库建立分支**

**git remote add** origin https://github.com/yourname/git-demo.git

**将本地 main 推送到 GitHub**

**git push -u** origin main(本地要推送的分支)





- 远程 HEAD 只是一个静态标记，告诉平台：默认打开、默认拉取的分支是哪一个

> 裸仓库（github 上的仓库都是 bare）：没有工作区，所以没有 “当前工作位置” 这个概念，它的 HEAD 仅仅是一个静态指向。