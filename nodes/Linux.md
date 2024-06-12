# Linux

> Linux是一种自由和开放源码的类UNIX操作系统。该操作系统的内核由林纳斯·托瓦兹在1991年10月5日首次发布，再加上用户空间的应用程序之后，就成为了Linux操作系统。Linux也是自由软件和开放源代码软件发展中最著名的例子。

--------------------------------------------------
## 基本命令

--------------------------------------------------
## 应用场景

--------------------------------------------------
### 查看进程的运行状态

通过 ```ps``` 命令来查看系统中进程的运行状态。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ps
  PID TTY          TIME CMD
 2135 pts/4    00:00:00 bash
 2210 pts/4    00:00:00 ps 
```

> Linux中的ps命令是Process Status的缩写。ps命令用来列出系统中当前运行的那些进程。ps命令列出的是当前那些进程的快照，就是执行ps命令的那个时刻的那些进程。

```ps -ef``` 用于查看系统的完整进程信息，其中 *-e* 参数用于显示所有进程，*-f* 参数指定以完整格式输出进程信息。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ps -ef
UID        PID  PPID  C STIME TTY          TIME CMD
root      1735     1  0  2023 ?        00:10:17 /usr/sbin/sshd -D
ubuntu   27197 27195  0 09:56 ?        00:00:00 bash
...
```

其中信息字段的意义为：
 * UID : 进程的所属用户
 * PID : 进程id
 * PPID : 父进程id
 * C : 进程占用的CPU百分比
 * STIME : 进程的启动时间
 * TIME : 该进程使用的CPU时间
 * CMD : 进程命令名称和参数

```ps -aux``` 是一个类似的等价命令，主要差别是信息的显示风格。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ps -aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      1735  0.0  0.0  72304  3128 ?        Ss    2023  10:17 /usr/sbin/sshd -D
ubuntu   27197  0.0  0.0  12368  3252 ?        Ss   09:56   0:00 bash
...
```

其中信息字段的意义为：
 * USER : 进程的所属用户名
 * PID : 进程id
 * %CPU : 进程占用的CPU百分比
 * %MEM : 进程占用的内存百分比
 * VSZ : 进程占用的虚拟内存(KB)
 * RSS : 进程占用的内存(KB)
 * STAT : 进程状态
 * START : 进程的启动时间
 * TIME : 该进程使用的CPU时间
 * COMMAND : 进程命令名称和参数

上述命令通常结合 ```grep``` 命令来筛选关注的目标进程。比如可以通过 ```ps -ef | grep python``` 来筛选 python 相关的进程。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ps -ef | grep python
ubuntu   17830  2135  0 16:32 pts/4    00:00:00 grep --color=auto python
ubuntu   18862     1  0 May24 ?        00:16:29 python a.py
ubuntu   31308     1  5 May24 ?        04:19:25 python b.py -f ./data.json
...
```

需要注意的是 *ps* 命令显示的是进程状态的快照，如果需要实时显示系统中运行的进程信息，可以使用 ```top``` 命令。

```sh
top - 19:39:27 up 251 days, 23 min,  0 users,  load average: 0.03, 0.04, 0.04
Tasks: 146 total,   1 running,  93 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.9 us,  0.6 sy,  0.0 ni, 96.3 id,  0.0 wa,  0.0 hi,  0.2 si,  0.0 st
KiB Mem :  7643148 total,   692772 free,  4442100 used,  2508276 buff/cache
KiB Swap:        0 total,        0 free,        0 used.  2882388 avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                                                        
31308 ubuntu    20   0 1588184 159160   7296 S   8.3  2.1 259:46.65 python
...   
```

--------------------------------------------------
### 检查进程的日志输出

通过检查进程的日志输出，可以观察进程/服务的运行状态和排查异常。

```tail -f [log_filepath]``` 命令用于输出指定文件的最后几行内容，*-f* 参数用于循环滚动输出。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ tail -f ./log/collector.log
[2024-05-27 20:42:04] - [Collector](collection): code(0895) - page(1800/2048) - data(143565/163813)
[2024-05-27 20:42:43] - [Collector](collection): code(0895) - page(2000/2048) - data(159519/163813)
[2024-05-27 20:42:57] - [Collector](collection): code(0895) - page(2048/2048) - data(163308/163813)
[2024-05-27 20:42:57] - [Collector](collection): code(0895) collected
[2024-05-27 20:43:00] - [Collector](collection): code(0898) - pages(839) - data(67115)
[2024-05-27 20:43:00] - [Collector](collection): database(./data/0898.db) connected
[2024-05-27 20:43:00] - [Collector](collection): code(0898) - page(0/839) - data(0/67115)
[2024-05-27 20:43:44] - [Collector](collection): code(0898) - page(200/839) - data(15998/67115)
...
```

```tail -n [num] [log_filepath]``` 通过指定 *-n* 参数来控制输出的日志行数。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ tail -n 5 ./log/collector.log
[2024-05-27 20:42:57] - [Collector](collection): code(0895) collected
[2024-05-27 20:43:00] - [Collector](collection): code(0898) - pages(839) - data(67115)
[2024-05-27 20:43:00] - [Collector](collection): database(./data/0898.db) connected
[2024-05-27 20:43:00] - [Collector](collection): code(0898) - page(0/839) - data(0/67115)
[2024-05-27 20:43:44] - [Collector](collection): code(0898) - page(200/839) - data(15998/67115)
```

当进程出现异常，可以通过 ```cat``` 结合 ```grep``` 命令查看指定的异常信息。

```sh
cat [log_filepath] | grep [key_string]
```

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ cat ./log/collector.log | grep "error"
[2024-05-27 14:53:23] - [Collector](collection): code(0855) error ...
[2024-05-27 15:15:54] - [Collector](collection): code(0865) error ...
[2024-05-27 15:22:23] - [Collector](collection): code(0868) error ...
[2024-05-27 15:38:03] - [Collector](collection): code(0877) error ...
...
```

当筛选后的数据显示过长时，可以考虑使用 ```more``` 命令来优化输出：

```sh
cat [log_filepath] | grep [key_string] | more
```

--------------------------------------------------
### 终止进程

```kill -9 <PID>``` 是常用于终止进程的命令，其中 ```-9``` 参数指定强制终止进程，由于是强制终止，因此可能导致一些副作用，比如进程的资源未释放等。

```kill``` 命令本质上是通过向目标进程发送信号来结束进程。使用 ```kill <PID>``` 命令会默认发送 *SIGTERM(15)* 信号，理想情况下，目标进程应该监听该信号，并在释放资源后主动退出。

```kill -l``` 用于查看支持的信号列表：

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ kill -l
 1) SIGHUP       2) SIGINT       3) SIGQUIT      4) SIGILL       5) SIGTRAP
 2) SIGABRT      7) SIGBUS       8) SIGFPE       9) SIGKILL     10) SIGUSR1
1)  SIGSEGV     12) SIGUSR2     13) SIGPIPE     14) SIGALRM     15) SIGTERM
2)  SIGSTKFLT   17) SIGCHLD     18) SIGCONT     19) SIGSTOP     20) SIGTSTP
3)  SIGTTIN     22) SIGTTOU     23) SIGURG      24) SIGXCPU     25) SIGXFSZ
4)  SIGVTALRM   27) SIGPROF     28) SIGWINCH    29) SIGIO       30) SIGPWR
5)  SIGSYS      34) SIGRTMIN    35) SIGRTMIN+1  36) SIGRTMIN+2  37) SIGRTMIN+3
6)  SIGRTMIN+4  39) SIGRTMIN+5  40) SIGRTMIN+6  41) SIGRTMIN+7  42) SIGRTMIN+8
7)  SIGRTMIN+9  44) SIGRTMIN+10 45) SIGRTMIN+11 46) SIGRTMIN+12 47) SIGRTMIN+13
8)  SIGRTMIN+14 49) SIGRTMIN+15 50) SIGRTMAX-14 51) SIGRTMAX-13 52) SIGRTMAX-12
9)  SIGRTMAX-11 54) SIGRTMAX-10 55) SIGRTMAX-9  56) SIGRTMAX-8  57) SIGRTMAX-7
10) SIGRTMAX-6  59) SIGRTMAX-5  60) SIGRTMAX-4  61) SIGRTMAX-3  62) SIGRTMAX-2
11) SIGRTMAX-1  64) SIGRTMAX
```

通过 ```kill -s <SIG> <PID>``` 可以向指定进程发送指定命令。

在需要批量终止进程的场景，可以用以下组合命令来实现：

```sh
ps -ef | grep <pattern> | awk '{print $2}' | xargs kill
```

其中 ```ps -ef | grep <pattern> ``` 用于从所有进程中根据 *pattern* 筛选出目标进程。

```awk '{print $2}'``` 用于打印目标进程的进程PID，即 *ps* 命令输出的第二列。

```xargs``` 命令着用于将管道数据转换成命令行参数(多行转多列)。


--------------------------------------------------
### 统计指定目录下的文件数

```sh
ls -l [dir] | grep ^- | wc -l
```

上述命令用于统计指定目录下的文件数，由三个命令通过 **管道符(|)** 复合而成，其中每个命令的作用如下：

* ```ls -l [dir]``` : 用于显示指定目录下的文件信息，*-l* 参数用于显示文件的详细属性信息：

```sh
total 11916
-rw-rw-r-- 1 ubuntu ubuntu    5166 May 24 10:33 xxx.py
-rw-rw-r-- 1 ubuntu ubuntu  374349 May 27 10:43 xxx.json
drwxrwxr-x 2 ubuntu ubuntu    4096 May 27 14:52 log
drwxrwxr-x 2 ubuntu ubuntu  135168 May 15 09:45 data
...
```

* ```grep ^-``` : 用于匹配以 **-** 开头的行：

```sh
-rw-rw-r-- 1 ubuntu ubuntu    5166 May 24 10:33 xxx.py
-rw-rw-r-- 1 ubuntu ubuntu  374349 May 27 10:43 xxx.json
```

* ```wc -l``` : *wc* 命令用于计算文件的字节数，字数或者行数，*-l* 参数用于计算行数，因此上述命令的最终结果为：

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ls -l | grep ^- | wc -l
2
```

通过替换 *grep* 命令的筛选条件，可以对上述命令进行灵活应用，比如统计 json 文件的数量：

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ ls -l | grep ".json$" | wc -l
1
```

--------------------------------------------------
### 查看系统/目录的磁盘占用情况

```df -lh``` 命令用于查看系统的磁盘占用情况，*-l* 参数指定仅显示本地文件系统，*-h* 参数指定以人类可读的格式显示结果。

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ df -lh
Filesystem      Size  Used Avail Use% Mounted on
udev            3.7G     0  3.7G   0% /dev
tmpfs           747M  8.9M  738M   2% /run
/dev/vda1        99G   72G   24G  76% /
tmpfs           3.7G   24K  3.7G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           3.7G     0  3.7G   0% /sys/fs/cgroup
tmpfs           747M     0  747M   0% /run/user/500
```

```df``` 命令通常用来查看系统的整体磁盘占用情况，如果想要查看指定目录的磁盘占用，可以使用 ```du``` 命令。

```sh
du -h --max-depth=[num] [dir]
``` 

上述 *du* 命令中 *-h* 指定以可读形式输出，并通过 *--max-depth* 控制指定的目录深度，使用样例如下：

```sh
(base) ubuntu@VM-16-41-ubuntu:~$ du -h --max-depth=1 .
27G     ./data
20K     ./__pycache__
236K    ./samples
712K    ./.git
16M     ./log
27G     .
```

