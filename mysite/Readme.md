# 总体：

# 开发文档

感谢使用我们组开发的火车票订票系统。
组长：陈伟哲  
组员：邓伟信，李照宇，余子涵


## 模块划分

| 模块                   | 成员           |
| ---------------------- | -------------- |
| 前端及网页设计         | 陈伟哲，邓伟信 |
| 前后端对接            | 邓伟信，李照宇       |
| 用户部分    | 李照宇         |
| B+树设计及火车部分 | 余子涵         |
| 车票部分 | 李照宇，余子涵     |



## 模块功能

B+树：      实现创建文件存储的B+树，插入，删除，查找及区间查找。
火车部分：实现车次添加，车次发售，车次查询，车次删除及车次修改。
用户部分：实现用户注册，用户登录，查询用户信息，修改用户信息及修改用户权限。
车票部分：实现车票查询，带中转查询车票，车票订购及车票退订。



## 类设计

### **B+树**

数据成员：path保存文件路径，bpt保存树相关信息，fp为文件指针，level为开关状态。

```c++
char path[512];
bpt_t bpt;
mutable FILE *fp;
mutable int level;
```

1.构造函数：用文件路径及判断是否清空的bool变量来构建B+树。

```C++
bplus_tree(const char *pa, bool force_empty = false) : fp(nullptr), level(0){...}
```

2.查找函数：利用search_index及search_leaf函数找到key值可能存在的块（叶子），在块中查找元素，若函数返回值为0，则表示搜索到元素。

```C++
off_t search_index(const key_type &key) const;
off_t search_leaf(off_t index, const key_type &key) const;
int search(const key_type& key, value_t *value) const;
```

3.插入函数：首先类似于search函数找到所在块（叶子），在块中查找元素，若元素已存在，则函数返回1；当叶子存储记录数小于树的阶数时可直接插入，否则分裂叶结点，并递归向上地对索引调整。插入成功时，函数返回0。

```c++
int insert(const key_type& key, const value_t& value)；
void insert_record_without_split(leaf_node_t *leaf, const key_type &key,
	const value_t &value);
void insert_key_to_index(off_t offset, const key_type &key, off_t oldchild,
	off_t newchild) ；
```

4.删除函数：类似于search函数找到叶节点后，首先判断待删记录是否存在，若不存在，则函数返回-1；将此纪录删除后，若叶子存储记录数过小（小于1/2的阶数，根节点需特判），则先从它的前后节点借记录，若borrow失败，则将它与它的前后节点合并，并递归向上地对索引调整。删除成功时，函数返回0。

```C++
int remove(const key_type & key);
bool borrow_key(bool from_right, leaf_node_t &to);
void merge_leaf(leaf_node_t *left, leaf_node_t *right);
void remove_from_index(off_t offset, internal_node_t &node, const key_type &key);
bool borrow_key(bool from_right, internal_node_t &to, off_t parent_offset);
void merge_index(internal_node_t &left, internal_node_t &right);
```

5.区间查找：搜索所有键值在[left, right]之间的元素，并存储于vector中。函数返回元素个数。

```
int search_range(const key_type &left, const key_type &right,
sjtu::vector<record_t> &trainid_sequence) const;
```


### **vector类**

用于bptree的区间查找。


### **restTicket类**

用于保存相关车次在某一日期的余票。

```c++
struct restTicket {
	short ticket[60][5];
	restTicket(){
		for (int j = 0; j < 59; ++j) {
			for (int k = 0; k < 5; ++k)
				ticket[j][k] = 2000;
		}
	}
};
```


### **train类**

数据成员：

```c++
mystring<20> train_id;
mystring<40> name;
char catalog;
mystring<20> name_price[5];
bool besaled;
short num_station;
short num_price;
train_station sta[60];
```

其中，station类保存了相关车次在每个站的信息，string类为自己定义的字符串类。

```c++
struct train_station {
	mystring<20> name;
	short day_in_offset;
	short day_out_offset;
	mystring<5> arrive;
	mystring<5> start;
	mystring<5> stopover;
	short num_price;
	float price[5];
	...
};
```

1.构造函数：根据传入信息来定义一个train。

```C++
train(const mystring<20> &id, const mystring<40> &na, const char &cat, int num_sta, int num_pri, const mystring<20>* name_pri, const train_station *s) :
num_station(num_sta), num_price(num_pri), train_id(id), name(na), catalog(cat)
{...}
```

2.发售：首先查看此车次是否已被发售，是则输出0；否则标记为已发售并将相关信息写入文件。

```c++
void sale_train(bplus_tree<char> &find_train, bplus_tree<char> &location)；
```

3.查询：首先查看此车次是否已被发售，若未发售则输出0；否则输出车次相关信息。

```c++
void query()；
```

4.修改：首先查看此车次是否已被发售，是则输出0；否则根据传入信息修改此车次。

```c++
bool modify(const mystring<40> &na, const char &cat, int num_sta, int num_pri,
            const mystring<20>* name_pri, const train_station *s)；
```

5.购票：首先判断购票操作是否合法，若非法则返回false。否则修改余票。

```c++
bool buy(int num, const mystring<20> &loc1, const mystring<20> &loc2,
         const mystring<10> &date, const mystring<20> &kind,
         bplus_tree<restTicket> &theRestTicket)；
```

6.退票：操作类似于购票。

```c++
bool refund(int num, const mystring<20> &loc1, const mystring<20> &loc2,
            const mystring<10> &date, const mystring<20> &kind, 						   bplus_tree<restTicket> &theRestTicket);
```

7.查票：首先搜索到车次相关站，再利用余票类查询车票信息。

```c++
void queryTicket(const mystring<20> &loc1, const mystring<20> &loc2,
				const mystring<10> &date, bplus_tree<restTicket> &theRestTicket);
```


### **User类**

数据成员：

```c++
struct User {
	mystring<20> id;
	mystring<40> name;
	mystring<20> password;
	mystring<20> email;
	mystring<20> phone;
	int intid;
	int privilege;
	...
};
```

1.构造：根据传入信息来构造一个User。

```c++
User(const mystring<40> &cname, const mystring<20> &cpassword, const mystring<20> &cemail, const mystring<20> &cphone) : name(cname), password(cpassword), email(cemail), phone(cphone), intid(-1), privilege(0);
```

2.注册：把用户信息写入文件。

```c++
void file_register(User &user);
```

3.登陆：首先判断用户是否合法，然后再将输入的密码和文件里存的用户密码做比较，如果相同返回1，否则返回0。

```c++
void file_login(const int cintid, const mystring<20> &cpassword);
```

4.查询：首先判断用户是否合法，然后再从文件里找到用户信息并输出。

```c++
void file_query_profile(const int cintid);
```

5.修改用户信息：首先判断用户是否合法，然后再从文件里找到用户信息并修改。

```c++
void file_modify_profile(const int cintid, const mystring<40> &cname, const mystring<20> &cpassword, const mystring<20> &cemail, const mystring<20> &cphone);
```

6.修改用户权限：首先判断管理员操作是否合法，然后再找到用户权限信息并修改。

```c++
void file_modify_priviledge(const int &id1, const int &id2, const int &privilege);
```


### **ticket类**

数据成员：

```c++
struct ticket {
	mystring<20> train_id;
	char catalog;
	mystring<20> loc1;
	mystring<20> loc2;
	mystring<10> date;
	mystring<20> ticket_kind[5];
	mystring<10> loc1date;
	mystring<5> loc1time;
	mystring<10> loc2date;
	mystring<5> loc2time;
	...
};
```

1.构造：在用户购票时构造，根据train_id在bptree中找到该车次信息构造一个ticket。

```c++
ticket(const mystring<20> &ctrain_id, const mystring<20> &cloc1, const mystring<20> &cloc2, const mystring<10> &cdate,
		const char &ccatalog, const mystring<10> &cloc1date, const mystring<5> &cloc1time, const mystring<10> &cloc2date,
		const mystring<5> &cloc2time, const int &cnum_kind)
		: train_id(ctrain_id), loc1(cloc1), loc2(cloc2), date(cdate), catalog(ccatalog), loc1date(cloc1date), loc1time(cloc1time), loc2date(cloc2date),
		loc2time(cloc2time), num_kind(cnum_kind);
```

2.购票：首先判断用户是否合法，然后再根据train_station类的购票操作返回值判断是否有余票，如果有则购票成功，否则购票失败。

```c++
void file_buy_ticket(const mystring<20> &id, const int &intid, const int &num, const mystring<20> &train_id,
	const mystring<20> &loc1, const mystring<20> &loc2, const mystring<10> &date,
	const int &intdate, const mystring<20> &ticket_kind, bplus_tree<train> &thetrain,
	bplus_tree<ticket> &theticket, bplus_tree<char> &find_ticket, bplus_tree<restTicket> &theRestTicket);
```

3.退票：首先判断用户是否合法，然后再根据train_station类的退票操作返回值判断是否可退票，如果可以在在bptree中找到该票信息，如果合法则退票成功，否则购票失败。

```c++
void file_refund_ticket(const int &num, const mystring<20> &id, const int &intid, const mystring<20> &train_id,
	const mystring<20> &loc1, const mystring<20> &loc2, const mystring<10> &date, const int &intdate,
	const mystring<20> &ticket_kind, bplus_tree<ticket> &theticket, bplus_tree<train> &thetrain, bplus_tree<restTicket> &theRestTicket);
```

4.查票：首先判断用户是否合法，然后再在bptree中利用区间搜索查找该用户所买的票，如果有票合法，则依次输出，否则查票失败。

```c++
void file_query_order(const mystring<20> &id, const int &intid, const mystring<10> &date, const mystring<10> &catalog,
	bplus_tree<ticket> &theticket, bplus_tree<char> &find_ticket);
```


### **mystring类**

数据成员：

```c++
template <int _size>
struct mystring {
	char str[_size + 1];
	int len, size;
	...
};
```

1.构造：支持默认构造和拷贝构造。

```c++
mystring();
mystring(const char *other);
mystring(const mystring &other);
```

2.比较：判断两个类两个字符串是否大小或是相等。

```c++
bool operator <(const mystring<_size> &s);
bool operator == (const char *tmp);
bool operator == (const mystring &tmp);
```

3.加法：将字符或字符串相加。

```c++
mystring operator += (char st);
template<int size1, int size2>
mystring<size1 + size2> operator +(const mystring<size1> &str1, const mystring<size2> &str2);
```

4.赋值

```c++
mystring<_size> & operator =(const mystring<_size> &s);
```

5.输出

```c++
friend ostream & operator << (ostream &os, const mystring &s);
```


## 文件设计

| 文件名         | 功能                                                         |
| -------------- | ------------------------------------------------------------ |
| thetrain.db    | 保存车次信息（key值为train_id, value为train类）              |
| location.db    | 保存所有站点（key值为station_name, value为一个 char）        |
| find_train.db  | 记录通过两站间的车次（key值为loc1+loc2+train_id, value为catalog） |
| restTicket.db  | 记录某车次某天余票情况（key值为date+train_id, value为restTicket类） |
| find_ticket.db | 根据车票类型查找车票（key值为user_id+date+train_id+loc1+loc2, value为ticket类）   |
| theticket.db   | 记录车票信息（key值为user_id+date+train_id+loc1+loc2, value为catalog）          |
| UserShelf      | 记录用户信息 （包括id, password, email, phone, privilege）           |

## 前端

### 文件具体到html

#### index.html

- 主页面

- 有部分引导内容

#### login.html

- 用于登录

- 会额外传出inputName和inputPassword两个内容用于登录。

#### signup.html

- 用于注册

#### Signupadmin.html

- 用于注册管理员

- 界面里有一个谷歌验证码

- 此页面提交的数据需要是中国大陆ip

#### SeekTrain.html

- 用于展示查找的车次，本页面同时兼顾查询直达和有中转的。

- 需要传入asked(True, False)。代表这个页面是否是查询过的页面。

- 需要传入Trains为set套set的形式，里层是每个火车的具体参数，外层是每辆火车。

- 会传出from, destination, dateoftrain用于查询，以及yzz的一个checkbox勾选选项帮助判断是否有中转

- 买票操作需要再完成

#### add_train*.html

- 用于添加车次

- 需要依次进入add_train add_train_in_class add_train_in_station三个html，每次submit后需要跳转到下一个html。

- 并在后两个中用到两个枚举变量num_price和num_station。

- 在add_train_in_station中需要有class_train这样一个set，从而保证其正确。

- add_train 传出 trainid,trainname,catalogs,num_station,num_price

- add_train_in_class 传出class_train表示等级的名字

- add_train_in_station 传出name_station time_arriv time_start time_stopover price[][] 这些值

- 以上的所有传输全部** 使用 ** cookie实现

#### AskTrain.html

- 用于查询车次

- 继承了query_train.html

- 已经公开过的车次公开按钮和删除按钮全部被删除

#### buyhistory.html

- 用于查询订票历史

- 在此页面退订车票

#### ChangeInfo.html

- 用于更改用户信息

#### ShowInfo.html

- 用于展示用户信息

- 如果你是管理员则会特殊提示

#### Error.html

- handle 404 与 500 用的

- 会自动跳转到主页

#### privilege.html

- 用于更改用户权限

- 一键修改， 操作简单
