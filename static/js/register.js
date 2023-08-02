
let vm = new Vue({
    // 通过ID选择器找到绑定的HTML的内容
    el:'#app',
    // 修改vue的模板语法
    delimiters:['[[',']]'],

    data:{
        // v-model
        username:'',
        password:'',
        password2:'',
        mobile:'',
        allow:'',
        image_code_url:'',
        uuid:'',
        image_code:'',
        sms_code:'',
        sms_code_tip:'获取短信验证码',
        send_flag:false, // 用来表示是否已经发送了短信验证码 ， false表示没有 ， true表示有

        // v-show
        error_name:false,
        error_password:false,
        error_password2:false,
        error_mobile:false,
        error_allow:false,
        error_image_code:false,
        error_sms_code:false,

        //  error_message  异常信息
        error_name_message:'',
        error_code_message:'',
        error_sms_code_message:'',
    },

    // 定义在这里里面的方法会在页面加载之后被调用
    mounted(){
        // 调用生成图片验证码
        this.generate_image_code();
    },

    // 定义绑定事件的方法 html中使用@blur绑定的事件
    methods:{
        // 检查短信验证码
        check_sms_code(){
            // 检查短信验证码的位数是否正确
            if(this.sms_code.length != 6){
                this.error_sms_code_message = '验证码输入有误';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        // 发送短信验证码
        send_sms_code(){
            // 判断是否已经请求发送短信验证码了
            if(this.send_flag == true){
                // 验证码已发送 ， 函数停止执行
                return;
            }
            this.send_flag = true;

            // 请求发送短信验证码的路由
            // ver/sms_code/mobile/?uuid&image_code
            let url = '/ver/sms_code/'+ this.mobile +'/?uuid='+ this.uuid +'&image_code='+ this.image_code;
            axios.get(
                url,
                {responseType:'json'}
            )
                // 请求成功
                .then(response =>{
                    // 实现60s倒计时
                    if(response.data.code == '0'){
                        console.log(60)
                        let number = 60;
                        // setInterval(回调函数 ， 时间间隔毫秒)
                        let t = setInterval(() => {
                            if(number == 1){
                                // 停止回调函数的执行
                                clearInterval(t);
                                sms_code_tip:'获取短信验证码';
                                // 重新生成一个图片验证码
                                this.generate_image_code();
                                // 设置允许继续发送请求
                                this.send_flag = false;
                            } else {
                                number -= 1;
                                this.sms_code_tip = number + 's';
                            }
                        } ,1000)
                    } else {
                        this.error_sms_code_message = response.data.errsg;
                        this.error_sms_code = true;
                        this.send_flag = false;
                    }
                })
                // 请求失败
                .catch(error =>{
                    console.log(error.response)
                    this.send_flag = false;
                })

        },

        // 生成图片验证码
        generate_image_code(){
            // 调用common中生成uuid的方法
            this.uuid = generateUUID();
            // /ver/image_code/14072742-4fb9-428d-8d3a-e304864b644d/
            this.image_code_url = '/ver/image_code/'+ this.uuid +'/'
        },
        // 校验图片验证码
        check_image_code(){
            if(this.image_code.length != 4){
                this.error_image_code = true;
                this.error_code_message = '图形验证码输入不正确';
            } else {
                this.error_image_code = false;
            }
        },

        // 校验用户名
        check_username(){
            // 定义用户名的规则
            let re=/^[a-zA-Z0-9-_]{5,20}$/;
            // 判断接收到的数据是否符合条件
            if(re.test(this.username)){
                // 表示匹配成功
                this.error_name = false
            } else {
                // 表示用户名不规范
                this.error_name = true;
                this.error_name_message = '用户名不规范，应当使用a-zA-Z0-9-_的组合'
            }

            // 判断用户是否合法
            if(this.error_name == false){
                // 校验用户名是否重复
                // 使用变量组合一个请求路径url
                let url = '/users/username/'+ this.username +'/count/';
                // 发送ajax请求
                // axios.get(url , 请求头(字典))
                axios.get(
                    url,
                    {responseType:'json'}
                )
                // 请求成功
                    .then(response => {
                        // 可以获取到后端传递过来的数据
                        if(response.data.count == 1){
                            // 用户已存在
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        }else {
                            this.error_name = false;
                        }
                    })
                // 请求不成功
                    .catch(error =>{
                        console.log(error.response)
                    })
            }
        },
        // 校验密码
        check_password(){
            let re=/^[a-zA-Z0-9]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 判断两次密码是否一致
        check_password2(){
            if(this.password == this.password2){
                this.error_password2 = false;
            } else {
                this.error_password2 = true;
            }
        },
        // 校验手机号
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        // 校验是否勾选协议
        check_allow(){
            if(!this.allow){
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },

        on_submit(){
            // 调用所有的方法
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();
            // 当有数据判断不正确 ， 不允许提交 ， 当v-show的数据为true时不允许提交
            if(this.error_name == true || this.error_password == true || this.error_password2 == true ||
                this.error_mobile == true || this.error_allow == true){
                // 禁用表单提交事件
                window.event.returnValue = false;
            }

        }
    }
})