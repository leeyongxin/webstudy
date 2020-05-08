var apiRoot = '.'
var app = new Vue({
  el: '#app',
  data: {
    ip: '10.1.10.9',
    alertModal: false,
    alertContent: 'sss',
    analog: [],
    digital: [],
    params: [],
    trigger: [],
    triggerParams: [],
    reset: [],
    resetParams: [],
    manualReset: [],
    paramsHide: [],
    trouble: [],
    activeTab: 'real',
    timer: null,
    disabled: false,
    btnTxt: '实时读取',
    activePower: '',
    reActivePower: '',
    spd: ''
  },
  methods: {
    start(type) {
      var self = this
      this.activeTab = 'real'
      if (self.timer != null && type == 1) {
        clearInterval(this.timer)
        this.timer = null
        this.btnTxt = '实时读取'
        this.disabled = false
      }
      if (self.timer != null && type == 2) {
        return
      }
      if (type == 3) {
        clearInterval(this.timer)
        this.timer = null
        this.btnTxt = '实时读取'
        this.disabled = false
        return
      }
      $.post(apiRoot + "/set", {
          ip: self.ip
        },
        function (data) {
          switch (data.code) {
            case 0:
              if (type == 1) {
                self.readInfo()
              }else if(type == 2) {
                self.alertTrigger()
                self.disabled = true
                self.btnTxt = '读取中..'
                self.timer = setInterval(self.readInfo, 1000)
              }
              break;
            case 100:
              self.alertTrigger('读取失败 ！！！')
              break;
            case 101:
              self.alertTrigger('读取失败 ！！！')
              break;
          }
        });
    },
    set(func) {
      var self = this
      $.post(apiRoot + "/set", {
        ip: self.ip
      },
      function (data) {
        switch (data.code) {
          case 0:
            func()
            break;
          case 100:
            self.alertTrigger('设置失败 ！！！')
            break;
          case 101:
            self.alertTrigger('设置失败 ！！！')
            break;
        }
      });
    },
    getParams() {
      var self = this
      $.post(apiRoot + "/set", {
        ip: self.ip
      },
      function (data) {
        switch (data.code) {
          case 0:
            $.get(apiRoot + "/params",function (data) {
              switch (data.code) {
                case 0:
                  self.analog = data.analog
                  self.digital = data.digital
                  self.params = data.params
                  break;
                case 100:
                  break;
              }
            });
            break;
          case 100:
            self.alertTrigger('读取失败 ！！！')
            break;
          case 101:
            self.alertTrigger('读取失败 ！！！')
            break;
        }
      });
    },
    getTypeData(type) {
      var self = this
      this.activeTab = type
      if ('analog' == type || type == 'digital') {
        this.activeTab = 'real'
      }
      

      $.post(apiRoot + "/set", {
        ip: self.ip
      },
      function (data) {
        switch (data.code) {
          case 0:
            $.get(apiRoot + "/type?type="+type,function (data) {
              switch (data.code) {
                case 0:
                  self[type] = data[type]
                  console.log(data[type])
                  break;
                case 100:
                  break;
              }
            });
            break;
          case 100:
            self.alertTrigger('读取失败 ！！！')
            break;
          case 101:
            self.alertTrigger('读取失败 ！！！')
            break;
        }
      });
    },
    alertTrigger(txt, status){
      const self = this
      this.alertContent = txt || '操作成功!'
      this.alertModal = status || true
      const timer = setTimeout(function () {
        self.alertModal = false
        clearTimeout(timer)
      }, 1000);
    },
    readInfo(){
      var self = this
      this.getTypeData('analog')
      setTimeout(function(){
        self.getTypeData('digital')
      }, 1000);
      
    },
    save() {
      $.get(apiRoot + "/save",function (data) {
        switch (data.code) {
          case 0:
            window.open(data.url)
            break;
          case 100:
            break;
        }
      });
    },
    ctrl(type) {
      var self = this
      $.post(apiRoot + "/ctrl",{
        ip: self.ip,
        ctrl: type
      }, function (data) {
        switch (data.code) {
          case 0:
            self.alertTrigger('下发命令成功 ！')
            break;
          default:
            self.alertTrigger('下发命令失败 ！！！')
            break;
        }
      });
    },
    write(type, ctrl, value) {
      var self = this
      $.post(apiRoot + "/write",{
        ip: self.ip,
        ctrl: ctrl,
        value: self[value],
        category: type
      }, function (data) {
        switch (data.code) {
          case 0:
            self.alertTrigger('下发命令成功 ！')
            break;
          default:
            self.alertTrigger('下发命令失败 ！！！')
            break;
        }
      });
    },
    params_write(item) {
      var self = this
      this.set(function(){
        $.post(apiRoot + "/params_write",{
          ip: self.ip,
          value: item.value,
          address: item.address,
          type: item.type
        }, function (data) {
          switch (data.code) {
            case 0:
              self.alertTrigger('下发命令成功 ！')
              break;
            default:
              self.alertTrigger('下发命令失败 ！！！')
              break;
          }
        });
      })
    }
  },
})