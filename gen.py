import os

tmpl_path="4k_get.xml"
head_tmpl='''
<?xml version="1.0" encoding="UTF-8" ?>
<workload name="Test-rgw-01" description="Test rgw">
    <workflow>
'''
tail_tmpl='''
    </workflow>
</workload>	
'''
init_tmpl='''
		<workstage name="init">
			<work name="init-01" type="init" workers="1" driver="driver1" config="cprefix=test;containers=r(1,360)">
				<storage type="s3" config="accesskey={access_key};secretkey={secret_key};endpoint=http://192.168.3.169:10001;"/>
			</work>
		</workstage>
'''

pre_work=''' \
		<workstage name="{name}">			
            {new_work}
		</workstage>
'''
work_desc=''' \
<work name="{name}" workers="{worker_num}" runtime="300">
				<storage type="s3" config="accesskey={access_key};secretkey={secret_key};endpoint=http://{host}:{port}" />
				<operation type="read" ratio="100" config="cprefix=test;oprefix=rgwobject;containers=r({c_start},{c_end});objects=r(1,1000)" />
			</work>
            {new_work}
            '''

load_work=''' \
            <work type="prepare" workers="2" driver="driver1" config="cprefix=test;oprefix=rgwobject;containers=r(1,60);objects=r(1,1000);sizes=c(4)KB" >
				<storage type="s3" config="accesskey=9YUURK872PWXYKX52H9P;secretkey=39YrdVYMi0BXaf31wdou1viuGSc5iO2D0JYFSaTP;endpoint=http://192.168.3.169:10001;"/>
			</work>
    '''
dispose_tmpl=''' \
    	<workstage name="dispose" closuredelay="0" config="">
			<auth type="none" config=""/>
            <work name="dispose-1" type="dispose" workers="2" driver="driver1" interval="5" division="container" runtime="0" rampup="0" rampdown="0" afr="0" totalOps="1" totalBytes="0" config="cprefix=test;containers=r(1,360);">
                <auth type="none" config=""/>
                <storage type="s3" config="accesskey={access_key};secretkey={secret_key};endpoint=http://{host}:{port};path_style_access=true"/>
            </work>
		</workstage>
    '''
hosts=['192.168.3.169','192.168.3.170','192.168.3.171']
port_cnt=100000
max_port_per_hosts=12
access_key=''
secret_key =''
default_host ='192.168.3.169'
default_port='10001'
def update_access(ss):
    return update_key_by_value(ss,'access_key',access_key)
def update_s_key(ss):

    return update_key_by_value(ss,'secret_key',secret_key)
def set_name(ss,name):
    return update_key_by_value(ss,'name',name)
def add_work(w_stage,nw):
    return update_key_by_value(w_stage,'new_work',nw)
def clean_work(ss):
    return update_key_by_value(ss,'new_work','')
def update_key_by_value(ss,key,val):
    ss=ss.replace('{'+key+'}',val)
    return ss
with open(tmpl_path,"w+") as f:
    f.write(head_tmpl)
    init_str= init_tmpl
    init_str =update_access(init_str)
    init_str =update_s_key(init_str)
    f.write(init_str)
    pre_str = pre_work
    nw = work_desc
    nw=update_access(nw)
    nw =update_s_key(nw)
    nw = set_name(nw,"prepare")
    pre_str = set_name(pre_str,'prepare')
    pre_str = add_work(pre_str,nw)
    pre_str = clean_work(pre_str)
    f.write(pre_str)
    
    load_str = pre_work
    load_str = update_key_by_value(load_str,'name','4k_get_test')
    p = 10000
    for h in hosts:

        nw = work_desc
        nw = update_access(nw)
        nw = update_s_key(nw)
        nw = update_key_by_value(nw,'name','get_1')
        nw = update_key_by_value(nw,'worker_num','2')
        nw = update_key_by_value(nw,'host',h)
        nw = update_key_by_value(nw,'port',str(p))
        p=p+1
        load_str = add_work(load_str,nw)
    load_str = clean_work(load_str)
    f.write(load_str)

    dipos_str= dispose_tmpl
    dipos_str = update_access(dipos_str)
    dipos_str = update_s_key(dipos_str)
    dipos_str = update_key_by_value(dipos_str,'host',default_host)
    dipos_str = update_key_by_value(dipos_str,'port',default_port)
    f.write(dipos_str)
    f.write(tail_tmpl)
    f.flush()

print("done!")
