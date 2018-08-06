# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy,requests,random,urllib,time
from scrapy.selector import Selector
#這个爬虫的前提是你要先登录前程无忧网，注意是填写验证码的那种登录，必须要退出你当前的登录状态重新登陆才行
class QianChengWuYouSpider(scrapy.Spider):
        name="qcwy"  #前程无忧爬虫
        allowed_domains=[]
        start_urls=[]
        header={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36Name"}
        def __init__(self):
            #self.loginQianChengWuYou()
            self.session = self.loginQianChengWuYou()
            self.searchQianChengWuYouJob("python开发工程师")
        def loginQianChengWuYou(self):
            wuYouSession = requests.session()
            url ="https://login.51job.com/login.php?lang=c"
            ts =""
            for x in range(10):
                c = random.randint(0,9)
                ts+=str(c)
            loginname ="用户名"
            password ="用户密码"
            realName ="真实的用户名"
            datas ={
                    'lang':'c',
                    'action':'save',
                    'from_domain':'i',
                    'loginname':loginname,
                    'password':password,
                    'verifycode':''
                    
                    }
            req = wuYouSession.post(url,data=datas,headers=self.header) 
            traceUrl ="http://my.51job.com/my/My_login_trace.php?url=http://i.51job.com/userset/my_51job.php"
            traceReq = wuYouSession.get(traceUrl,headers=self.header)   
            resumeUrl ="http://i.51job.com/userset/my_51job.php"
            req = wuYouSession.get(resumeUrl,headers=self.header)
            res = req.content
            response =res.decode("gbk")
            
            if realName in response:
                print("登录前程无忧成功")
                return wuYouSession
            else:
                print("登录前程无忧失败")
                return None
        
        def parse(self,response):
                res = response.body.decode("gbk")
                selector = Selector(text=res)
                spans = selector.xpath('//p[@class="t1 "]/span/a/@href').extract()
                spanSize = len(spans)
                print(spanSize)
                if len(spans) >0:
                    for x in spans:
                        print(x)
                        self.getQianChengWuYouJobMessage(x,self.session)
                        time.sleep(5)
        def searchQianChengWuYouJob(self,key):
            for x in range(1,4):
                url ="http://search.51job.com/list/040000,000000,0000,00,9,99,"+urllib.parse.quote(key)+",2,"+str(x)+".html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=4&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
                self.start_urls.append(url)
                
                
        def getQianChengWuYouJobMessage(self,url,session):
            res = session.get(url,headers=self.header)
            if res.status_code ==200:
                response = (res.content).decode("gb2312","ignore")
                responseStamp = int(time.time()*1000)
                selector = Selector(text=response)
                jobids =selector.xpath('//a[@class="icon_b i_upline"]/@id').extract()
                imagepaths = selector.xpath('//a[@class="but_sq"]/img/@src').extract()
                jobnames = selector.xpath('//div[@class="cn"]/h1/@title').extract()
                companynames = selector.xpath('//p[@class="cname"]/a/@title').extract()
                if len(jobids) ==1 and len(imagepaths) ==1 and len(jobnames) ==1 and len(companynames) ==1:
                    jobid =jobids[0]
                    imageresult = imagepaths[0]
                    jobname = jobnames[0]
                    companyname = companynames[0]
                    if "im/jobs" in imageresult:
                        imagepath=imageresult.split("im/jobs")[0]
                        print(jobid,imagepath)
                        self.sendQianChengWuYouResume(jobid, imagepath, responseStamp, self.session,jobname,companyname)
                        
        def sendQianChengWuYouResume(self,jobid,imagepath,timestamp,session,jobname,companyname):
            rand =self.getRand()
            strTime = int(time.time()*1000)
            url ="http://i.51job.com/delivery/delivery.php?rand="+rand+"&jsoncallback=jsonp"+str(timestamp)+"&_="+str(strTime)+"&jobid=("+str(jobid)+":0)&prd=search.51job.com&prp=01&cd=jobs.51job.com&cp=01&resumeid=&cvlan=&coverid=&qpostset=&elementname=hidJobID&deliverytype=1&deliverydomain=http://i.51job.com&language=c&imgpath="+imagepath
            print(url)
            res = session.get(url,headers=self.header)
            response = res.text
            #print(response)
            if "投递成功" in response:
                 print("成功投递"+companyname+"的"+jobname+"岗位")
            elif "申请中包含已申请过的职位，7天内不可重复申请" in response:
                print("改公司的岗位你已经投递过了，7天内不可重复投递")
            else:
                print("投递"+companyname+"的"+jobname+"岗位失败")
        def getRand(self):
            numbers=[0,1,2,3,4,5,6,7,8,9]
            rand ="0."
            for x in range(16):
                rin = random.randint(0,9)
                rand+=str(numbers[rin])
            return rand