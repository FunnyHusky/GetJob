# -*- coding:UTF-8 -*-
import scrapy,csv,requests,random,urllib
from zhilianzhaoping.items import ZhilianzhaopingItem
from scrapy.selector import Selector
import re
import time
import random
#当前這个爬虫无法处理新版本的登录，所以這个爬虫基本上已经废了，除非你可以在登录后获取cookie，把cookie写进请求头中可以跳过登陆步骤
class zlzpSpider(scrapy.Spider):
    name ="zhilian"   #爬虫名
    allowed_domains=[]  #只能爬取这个网址开头的网站
    start_urls=[]
    header={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36Name"}
    
    def __init__(self):
       self.session =self.loginZhiLianZhaoPing()
       self.getZhiLianJobUrl("深圳","python开发工程师")
    def parse(self,response): #解析response
        res = response.body.decode("UTF-8")
        selector = Selector(text=res)
        jobs = selector.xpath('//a[@style="font-weight: bold"]/@href').extract()
        pars = selector.xpath('//a[@style="font-weight: bold"]/@par').extract()
        companys = selector.xpath('//td[@class="gsmc"]/a[1]/text()').extract()
        jobsize = len(jobs)
        parsize = len(pars)
        comsise = len(companys)
        print(jobsize,",",parsize,",",comsise)
        if jobsize ==parsize and jobsize==comsise and jobsize >0:
            for x in range(jobsize):
                parUrl = jobs[x]+"?"+pars[x]
                print(companys[x],",",parUrl)
                self.sendResume(parUrl,self.session)
    def loginZhiLianZhaoPing(self):  #登录智联招聘
        username ="用户名"
        password ="用户密码"
        session =requests.session()
        realName ="你的真实名字"
        url ="https://passport.zhaopin.com/account/login" 
        datas ={
            'int_count':999,
            'errUrl':'https://passport.zhaopin.com/account/login',
            'RememberMe':'true',
            'requestFrom':'portal',
            'loginname':username,
            'Password':password } 
        req = session.post(url,headers=self.header,data=datas,verify=False)
        if req.status_code ==200:
            res = req.text
            if realName in res:        
                print("登录成功，开始搜索职位")
                return session
    def getZhiLianJobUrl(self,city,jobname): #获取工作url
        s =[0,1,2,3,4,5,6,7,8,9,0,'q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m']
        result =''
        for x in range(32):
            rin = random.randint(0,35)
            result+=str(s[rin])
        url ="http://sou.zhaopin.com/jobs/searchresult.ashx?jl="+urllib.parse.quote(city)+"&kw="+urllib.parse.quote(jobname)+"&sm=0&sg="+result
        for x in range(1,3):
            pageStr = "&p="+str(x)
            self.start_urls.append(url+pageStr)
    def sendResume(self,url,session):#发送简历
        for x in range(5):
            res = session.get(url,headers=self.header,verify=False)
            if res.status_code ==200:
                response = res.text
                arrpattern ='.*?var arrVarFromASP = (.*?);.*?var ApplyUrl'
                tjUrlPattern ='.*?var tjUrl = (.*?);.*? var dateRefreshUrl'
                companyPattern=' var Str_CompName = "(.*?)";'
                res =re.findall(arrpattern, response, re.S)
                tjRes = re.findall(tjUrlPattern, response, re.S)
                companyRes = re.findall(companyPattern,response,re.S)
                if len(res) ==1 and len(tjRes) ==1 and len(companyRes) ==1:
                    realRes = res[0]
                    realTjRes = tjRes[0]
                    companyName = companyRes[0]
                    res = eval(realRes)
                    id = res[1]
                    name = res[2]
                    callbackUrl = res[3]
                    subtypePattern ='&subtype=(.*?)&cityid'
                    subtype = re.findall(subtypePattern,realTjRes,re.S)[0]
                    print(subtype)
                    if id !="" and name !="" and callbackUrl !="" and subtype !="" and companyName !="":
                        self.getJson(session, id, callbackUrl, subtype, name,companyName)
                        break
                else:
                    continue
            else:
                continue
    def getJson(self,session,id,relurl,subtype,jobname,companyname):
        print("当前正在投递  "+jobname)
        miss =int(time.time()*1000) 
        letters =[1,2,3,4,5,6,7,8,9,0,'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','z','t','u','v','x','w','y']
        letter =""
        for x in range(6):
            rin = random.randint(0,35)
            cr =letters[rin] 
            letter+=str(cr)
        #请求重要数据的网址
        url ="https://my.zhaopin.com/v5/FastApply/resumeinfo.aspx?t=1&j="+id+"_03_201_1_3_&j2=&so=&su=&ff=&fd=&c=jsonp"+letter+"&_="+str(miss)
        print(url)
        res = session.get(url,headers=self.header,verify=False)
        response =res.text
        print(response)
        d =response.split(",")
        if len(d) ==11:
            paravalue =(d[5].replace("\"","")).split("paravalue:")[1]
            print(paravalue)
            delerverUrl ="https://my.zhaopin.com/jobseeker/req_vacancy_ok.asp?"+paravalue+"jt="+jobname+"&subjobtype="+subtype+"|765&jdr=&ref="+relurl+"&applyType=0"
            for x in range(3):
                ress = session.get(delerverUrl,headers=self.header,verify=False)
                if "职位申请成功" in ress.text:
                    with open("C:\\Users\\liangzi\\Desktop\\spiderHistory\\zhilian"+str(time.strftime("%Y-%m-%d"))+".txt","a+",encoding="utf-8") as f:
                        f.write(time.strftime("%H-%M-%S")+":投递"+companyname+" "+jobname+"   成功 ")
                        f.write("\n")
                        print("投递  "+jobname+" 成功")
                    break;
                else:
                    with open("C:\\Users\\liangzi\\Desktop\\spiderHistory\\zhilian"+str(time.strftime("%Y-%m-%d"))+".txt","a+",encoding="utf-8") as f:
                        f.write(time.strftime("%H-%M-%S")+":投递"+companyname+" "+jobname+"   失败 ")
                        f.write("\n")
                        
                    time.sleep(2)
                    continue