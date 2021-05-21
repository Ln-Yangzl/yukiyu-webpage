#from flaskr.databaseCURD import checkValibleTableName
import pymysql
import traceback
from pymysql import cursors
from werkzeug.security import check_password_hash, generate_password_hash
from itertools import chain


#默认创建普通用户，授权select
def createUser(name,password):
    returnStatus=1
    db = pymysql.connect(host="localhost", port=3306, db="mysql", user="jhchen", password="123456",charset='utf8')
    cursor = db.cursor()
    host = '%'
    sql1 = "create user '%s'@'%s' identified by '%s';"%\
        (name,host,password)
    sql11="grant select on yukiyu.* to '%s'@'%s';"%\
    (name, host)
   
    cursor.execute("select user from db")
    elems = cursor.fetchall()
    res = list(chain.from_iterable(elems))
    print(res)
    if name in res:
        print("用户%s已存在"/(name))
        return 0

    try:
        print('start to execute:')
        print(sql1)
        print(sql11)
        cursor.execute(sql1)
        cursor.execute(sql11)
        print('create success !')
    except:
        print('create user error!')
        db.rollback()
        traceback.print_exc()
        returnStatus=0
    db.close()


    #在yukiyu库中的user插入同样
    db = pymysql.connect(host="localhost", port=3306, db="yukiyu", user="jhchen", password="123456",charset='utf8')
    cursor=db.cursor()
    data = privilegeOfUser(name)
    priv = data['privilege']
    sql2 = """
    insert into user_list(name,password,privilege) 
    values
    ('%s','%s','%s');"""%\
    (name,generate_password_hash(password),priv)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('insert success !')
    except:
        print('insert error!')
        db.rollback()
        traceback.print_exc()
        returnStatus=0

    cursor.close()
    db.close()
    return returnStatus

#删除用户
def dropUser(name):
    returnStatus=1
    db = pymysql.connect(host="localhost", port=3306, db="mysql", user="jhchen", password="123456",charset='utf8')
    cursor = db.cursor()
    host = '%'
    sql="drop user '%s'@'%s';"%\
    (name,host)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        db.commit()
        print('drop success !')
        returnStatus=1
    except:
        print('drop user error!')
        db.rollback()
        traceback.print_exc()
        returnStatus =0

    sql2 = """
    delete from yukiyu.user_list
    where name = '%s';
    """%\
    (name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('delete user success !')
    except:
        print('delete user error!')
        db.rollback()
        traceback.print_exc()
        returnStatus=0


    cursor.close()
    db.close()

    return returnStatus


def ifManage(name):
    db = pymysql.connect(host="localhost", port=3306, db="yukiyu",user="jhchen", password="123456", charset="utf8")
    sql = """
        select if_manager 
        from user_list
        where name = '%s';
    """%\
        (name)
    cursor=db.cursor(pymysql.cursors.DictCursor)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        print('success !')
    except:
        print('error!')
        traceback.print_exc()
    
    return data[0]['if_manager']


#授权为管理员用户，实现所有权限
def grantSuperUser(name):
    if ifManage(name)=='Y':
        print("success")
        return 1

    host='%'
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor = db.cursor()
    sql="""
    grant all privileges on yukiyu.* to '%s'@'%s';
    """%\
    (name,host)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        db.commit()
        print('grant success !')
    except:
        print('grant error!')
        db.rollback()
        traceback.print_exc()
        return 0


    data = privilegeOfUser(name)
    priv = data['privilege']
    sql2 = """
    update yukiyu.user_list
    set privilege = '%s'
    where name = '%s';
    """%\
    (priv,name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        db.rollback()
        traceback.print_exc()
        return 0

    sql3 = """
        update yukiyu.user_list
        set if_manager = 'Y'
        where name = '%s';
    """%\
        (name)
    try:
        print('start to execute:')
        print(sql3)
        cursor.execute(sql3)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        db.rollback()
        traceback.print_exc()
        return 0


    cursor.close()
    db.close()
    return 1

#授权为普通用户，select权限
def grantOrdinartUser(name):

    if(ifManage(name)=='N'):
        print("grant success")
        return 1
    

    host = '%'
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor = db.cursor()
    sql1="revoke all privileges on yukiyu.* from '%s'@'%s';"%\
    (name,host)
    sql11="grant select on yukiyu.* to '%s'@'%s';"%\
        (name,host)
    try:
        print('start to execute:')
        print(sql1)
        print(sql11)
        cursor.execute(sql1)
        cursor.execute(sql11)
        db.commit()
        print('revoke success !')
    except:
        print('revoke error!')
        db.rollback()
        traceback.print_exc()
        return 0

    sql2 = """
    update yukiyu.user_list
    set privilege = 'YNNN'
    where name = '%s';
    """%\
        (name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        db.rollback()
        traceback.print_exc()
        return 0



    sql3 = """
        update yukiyu.user_list
        set if_manager = 'N'
        where name = '%s';
    """%\
        (name)
    try:
        print('start to execute:')
        print(sql3)
        cursor.execute(sql3)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        db.rollback()
        traceback.print_exc()
        return 0

    #changePrivilege(name, 'YYYY')
    
    cursor.close()
    db.close()


# 查看指定权限
def checkOnePriv(name, privilege):
    s = privilege+'_priv'
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor=db.cursor(pymysql.cursors.DictCursor)
    sql = """
        select %s_priv
        from db
        where Db = 'yukiyu' and User = '%s';
    """%\
    (privilege,name)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        print('success !')
    except:
        print('error!')
        db.rollback()
        traceback.print_exc()
    
    return data[0][s]


#为指定用户增加指定权限
def addPrivForUser(name,privilege):

    
    if checkOnePriv(name,privilege)=='Y':
        print("succsee")
        return 1


    host='%'
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor = db.cursor()
    sql1 = "grant %s on yukiyu.* to '%s'@'%s';"%\
        (privilege,name,host)
    try:
        print('start to execute:')
        print(sql1)
        cursor.execute(sql1)
        db.commit()
        print('grant success !')
    except:
        print('grant error!')
        traceback.print_exc()

    data = privilegeOfUser(name)
    priv = data['privilege']
    sql2 = """
    update yukiyu.user_list
    set privilege = '%s'
    where name = '%s';
    """%\
    (priv,name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        traceback.print_exc()
    
    cursor.close()
    db.close()
    return 1

#删除指定用户的某权限
def delPrivForUser(name,privilege):

    if(checkOnePriv(name , privilege)=='N'):
        print("success")
        return 1

    host='%'
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor = db.cursor()
    sql1 = "revoke %s on yukiyu.* from '%s'@'%s';"%\
        (privilege,name,host)
    try:
        print('start to execute:')
        print(sql1)
        cursor.execute(sql1)
        db.commit()
        print('grant success !')
    except:
        print('grant error!')
        traceback.print_exc()
    
    data = privilegeOfUser(name)
    priv = data['privilege']
    sql2 = """
    update yukiyu.user_list
    set privilege = '%s'
    where name = '%s';
    """%\
    (priv,name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('update success !')
    except:
        print('update error!')
        traceback.print_exc()

    cursor.close()
    db.close()


#查询指定用户权限
def privilegeOfUser(name):
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor=db.cursor(pymysql.cursors.DictCursor)
    sql = """
        select User, select_priv, insert_priv, update_priv, delete_priv, create_priv, drop_priv
        from db
        where Db = 'yukiyu' and User = '%s';
    """%\
    (name)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        print('success !')
    except:
        print('error!')
        traceback.print_exc()
    
    data = cursor.fetchall()

    a=data[0]["select_priv"]
    b=data[0]["insert_priv"]
    c=data[0]["update_priv"]
    d=data[0]["delete_priv"]

    s=a+b+c+d

    dict = {'name': data[0]['User'],'privilege':s}

    print(dict)
    return dict



#查看所有用户及权限
def privilegeOfAllUser():
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor=db.cursor(pymysql.cursors.DictCursor)

    sql = """
        select User, select_priv, insert_priv, update_priv, delete_priv, create_priv, drop_priv
        from db
        where Db = 'yukiyu';
    """
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        print('success !')
    except:
        print('error!')
        traceback.print_exc()

    data = cursor.fetchall()
    cursor.close()
    db.close()
    list = []
    for item in data:
        a=item['select_priv']
        b=item['insert_priv']
        c=item['update_priv']
        d=item['delete_priv']
        s=a+b+c+d
        list.append({'name': item['User'],'privilege':s})


    print(list)
    return list

def printAllUser():
    db = pymysql.connect(host="localhost", port=3306, db="mysql",user="jhchen", password="123456", charset="utf8")
    cursor=db.cursor(pymysql.cursors.DictCursor)
    sql = "select if_manager, user_id, name, privilege  from yukiyu.user_list;"
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        print('success !')
    except:
        print('error!')
        traceback.print_exc()
    data = cursor.fetchall()
    print(data)

#返回用户密码hash值
def getPassword(name):
    db = pymysql.connect(host="localhost", port=3306, db="yukiyu",user="jhchen", password="123456", charset="utf8")
    cursor=db.cursor(pymysql.cursors.DictCursor)
    sql = "select password from yukiyu.user_list where name = '%s'"%\
        (name)
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        print('success !')
    except:
        print('error!')
        traceback.print_exc()
    
    data = cursor.fetchall()
    password_hash = data[0]['password']
    
    print(password_hash)
    return password_hash


def changePrivilege(name,priv):
    
    if priv[0]=='Y':
        addPrivForUser(name,'select')
    else:
        delPrivForUser(name,'select')

    if priv[1]=='Y':
        addPrivForUser(name,'insert')
    else:
        delPrivForUser(name,'insert')
    
    if priv[2]=='Y':
        addPrivForUser(name,'delete')
    else:
        delPrivForUser(name,'delete')

    if priv[3]=='Y':
        addPrivForUser(name,'update')
    else:
        delPrivForUser(name,'update')
    
    return 1



#包装函数
# info中的password为明文密码
# info = ['Y',id,'name','password','priv']
def commmitChangeToUserlist(oldInfo, newInfo):
    db = pymysql.connect(host="localhost", port=3306, db="yukiyu", user="jhchen", password="123456",charset='utf8')
    if checkValible(newInfo)==0:
        print('newInfo error')
        return -1
    

    sql1 = "savepoint x;"
    cursor=db.cursor()
    cursor.execute(sql1)
    print(sql1)

    if oldInfo == None:
        print('insert')
        returnStatus = insertItem(newInfo)
    elif newInfo==None:
        print('delete')
        returnStatus = deleteItem(oldInfo)
    else:
        print('update')
        returnStatus = updateItem(newInfo, oldInfo)
    
    if(returnStatus==0):
        print('error')
        sql2 = "rollback to x;"
        cursor.execute(sql2)
        db.commit()
        print(sql2)

    sql3="release savepoint x;"
    cursor.execute(sql3)
    db.commit()
    print(sql3)

    return returnStatus


def checkValible(info):
    if info==None:
        return 1
    ifManage = info[0]
    name = info[2]
    password = info[3]
    privilege = info[4]
    if ifManage=='Y' and privilege != 'YYYY':
        print('privilege error!')
        return 0
    
    return 1

#插入新用户
def insertItem(newInfo):
    status=1
    ifManage = newInfo[0]
    name = newInfo[2]
    password = newInfo[3]
    privilege = newInfo[4]

    status = createUser(name,password)
    if(status==0):
        return 0

    if(ifManage=='Y'):
        status= grantSuperUser(name)
    else:
        status = grantOrdinartUser(name)
    
    if status==0:
        return 0

    status = changePrivilege(name,privilege)
    if status==0:
        return 0
    
    print('insert item success')
    return 1

# 删除某用户
def deleteItem(oldInfo):
    status=1
    name = oldInfo[2]

    status = dropUser(name)

    if status==0:
        print('delete item error')
        return 0
    
    print('delete item success')
    return status

#更新信息

def updateItem(newInfo, oldInfo):
    returnStatus = 1

    nifManage=newInfo[0]
    nname=newInfo[2]
    npassword=newInfo[3]
    npriv=newInfo[4]

    oifManage=oldInfo[0]
    oname=oldInfo[2]
    opassword=oldInfo[3]
    opriv=oldInfo[4]
    
    if(npriv != opriv):
        returnStatus = changePrivilege(oname,npriv)
        if returnStatus == 0:
            print('change privilege error')
            return 0
        print('change privilege success')
    if(nifManage!=oifManage):
        returnStatus = changeIfManage(oname,nifManage)
        if returnStatus == 0:
            print('change ifManager error')
            return 0
        print('change ifManager success')
    if(npassword!=opassword):
        returnStatus = changePassword(oname,npassword)
        if returnStatus == 0:
            print('change password error')
            return 0
        print('change password success')
    if(oname != nname):
        returnStatus = changeName(oname,nname)
        if returnStatus == 0:
            print('change name error')
            return 0
        print('change name success')

    print('update item success')
    return returnStatus


#用户改姓名
def changeName(oname,nname):
    db = pymysql.connect(host="localhost", port=3306, db="mysql", user="jhchen", password="123456",charset='utf8')
    cursor=db.cursor()

    sql1 = """
    update user 
    set user='%s' 
    where user = '%s';"""%\
        (nname, oname)
    try:
        print('start to execute:')
        print(sql1)
        cursor.execute(sql1)
        db.commit()
        print('success !')
        returnStatus = 1
    except:
        print('updata user error !')
        db.rollback()
        traceback.print_exception()
        returnStatus = 0
        return returnStatus

    sql2="""
    update yukiyu.user_list 
    set name = '%s'
    where name = '%s';"""%\
        (nname,oname)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('success !')
        returnStatus = 1
    except:
        print('updata user error !')
        db.rollback()
        traceback.print_exception()
        returnStatus = 0
        return returnStatus

    return 1

# 用户改管理权限
def changeIfManage(name,nIfMnage):
    db = pymysql.connect(host="localhost", port=3306, db="mysql", user="jhchen", password="123456",charset='utf8')
    cursor=db.cursor()

    if(nIfMnage=='Y'):
        returnStatus = grantSuperUser(name)
    else:
        returnStatus = grantOrdinartUser(name)

    
    return returnStatus

#用户改密码
def changePassword(name,password):
    db = pymysql.connect(host="localhost", port=3306, db="mysql", user="jhchen", password="123456",charset='utf8')
    cursor = db.cursor()

    sql = "ALTER USER '%s'@'%s' IDENTIFIED WITH mysql_native_password BY '%s';"%\
        (name,'%',password)
    
    try:
        print('start to execute:')
        print(sql)
        cursor.execute(sql)
        db.commit()
        print('success !')
        returnStatus = 1
    except:
        print('updata error !')
        db.rollback()
        traceback.print_exception()
        returnStatus = 0

    if(returnStatus==0):
        return returnStatus

    password_hash = generate_password_hash(password)
    sql2 = """
    update yukiyu.user_list
    set password = '%s'
    where name = '%s';
    """%\
        (password_hash,name)
    try:
        print('start to execute:')
        print(sql2)
        cursor.execute(sql2)
        db.commit()
        print('success !')
        returnStatus = 1
    except:
        print('updata error !')
        db.rollback()
        traceback.print_exception()
        returnStatus = 0

    db.close()
    return returnStatus

def test1():
    
    newInfo = ['N','xx','123456','YNNN']
    commmitChangeToUserlist(None,newInfo)
    print('success')
    return

def test2():
    oldInfo = ['N','xx','123456','YNNN']
    newInfo = ['Y','xx','123456','YYYY']
    commmitChangeToUserlist(oldInfo,newInfo)

def test3():
    oldInfo = ['Y','xx','123456','YYYY']
    newInfo = ['N','xx','123456','YNNN']
    commmitChangeToUserlist(oldInfo,newInfo)

def test4():
    oldInfo = ['N','xx','123456','YNNN']
    commmitChangeToUserlist(oldInfo,None)

def test5():
    oldInfo = ['N','xx','123456','YNNN']
    newInfo = ['N','xxyy','123456789','YNNN']
    commmitChangeToUserlist(oldInfo,newInfo)


if __name__ == '__main__':
    #dropUser('xx')
    #test1()
    #test2()
    #test3()
    #test4()

    test5()
    
    db = pymysql.connect(host="localhost", port=3306, db="yukiyu", user="jhchen", password="123456",charset='utf8')
    #dropUser('xxx')
    #createUser('xxx','123456')
    #grantSuperUser('cy')
    #grantOrdinartUser('cyy')
    #addPrivForUser('cyy','delete')
    #delPrivForUser('cyy','delete')
    #privilegeOfAllUser()
    #privilegeOfUser('cyy')
    
    # printAllUser()
    # getPassword('xxx')

    db.close()