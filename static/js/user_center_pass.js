let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        old_password: '',
        new_password: '',
        new_password2: '',
        error_old_password: false,
        error_new_password: false,
        error_new_password2: false,

        error_new_password_message: '',
    },
    methods: {
        // 检查旧密码
        check_old_password(){
        	let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.old_password)) {
                this.error_old_password = false;
            } else {
                this.error_old_password = true;
            }
        },
        // 检查新密码
        check_new_password(){
            // 新旧密码不能一直
            if (this.old_password == this.new_password) {
                this.error_new_password = true;
                this.error_new_password_message = '新密码不能和旧密码一致';
            } else {
                this.error_new_password = false;
            }
        	let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.new_password)) {
                this.error_new_password = false;
            } else {
                this.error_new_password = true;
                this.error_new_password_message = '密码最少8位，最长20位';
            }
        },
        // 检查确认密码
        check_new_password2(){
            if (this.new_password != this.new_password2) {
                this.error_new_password2 = true;
            } else {
                this.error_new_password2 = false;
            }
        },
        // 提交修改密码
        on_submit(){
            this.check_old_password();
            this.check_new_password();
            this.check_new_password2();

            if (this.error_old_password==true || this.error_new_password==true || this.error_new_password2==true) {
                // 不满足修改密码条件：禁用表单
				window.event.returnValue = false
            }
        },
    }
});