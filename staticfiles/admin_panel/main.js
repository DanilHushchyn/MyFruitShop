function check_authenticated() {
    if(authenticated==='False'){
        Swal.fire({
          position: 'center',
          icon: 'error',
          title: 'Авторизуйтесь пожалуйста',
          showConfirmButton: false,
          timer: 1500
        })
        return false;
    }
    return true
}
let chat = $('.communication-chat')
let chatBtnSend = $('.send-msg')
let chatInput = $('.msg-input')
chat[0].scrollTo(10, chat[0].scrollHeight);
let socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
    );

socket.onmessage = (e) => {
    let message = JSON.parse(e.data)['message'];
    let element;
    // let message;
    // chat.empty()
    // for (let key in messages){
    //     message = messages[key]
        element = $(`
        <div class="direct-chat-msg">
            <div class="direct-chat-infos clearfix">
                <span class="direct-chat-name float-left"> ${message["user"]}</span>
                <span class="direct-chat-timestamp float-right"> ${new Date(message['timestamp']).toLocaleTimeString('ru-RU',{
                    "hour":'numeric',
                    "minute":'numeric',
                    "second":'numeric',
                }) }

                </span>
            </div>
            <img class="direct-chat-img" src="${avatar}" alt="Message User Image">


            <div class="direct-chat-text">
                ${ message['content'] }
            </div>
        </div>
        `)
        chat.append(element)
        chat.children().first().remove()
    // }
    chat[0].scrollTo(10, chat[0].scrollHeight);
}
socket.onclose = (e) => {
    console.log("Socket closed!");
}
chatInput.bind('keypress', function(e) {
    if(e.keyCode===13){
        chatBtnSend.click()
    }
});
chatBtnSend.on('click',function () {
    socket.send(JSON.stringify(
        {
            message: chatInput.val()
        }
    ))
    chatInput.val('')
})
//Balance WebSocket
let balanceBtn = $('.balance_btn')
let balanceInput = $('#exampleInputBalance')
let balance_socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/balance/'
);
balance_socket.onmessage = (e) => {
    let balance = JSON.parse(e.data)['balance'];
    let status = JSON.parse(e.data)['status'];
    let message = JSON.parse(e.data)['message'];
    Swal.fire({
          position: 'center',
          icon: status ?'success':'error',
          title: message,
          showConfirmButton: false,
          timer: 1500
    })
    if(status) {
        $(".balance_view").html(balance)
    }
}
balance_socket.onclose = (e) => {
    console.log("Balance socket closed!");
}
balanceInput.bind('keyup', function(e) {
    if (this.value < 1 || Number(this.value) === 0) {
        this.value = ''
    }
})
balanceBtn.on('click','.plus_btn, .minus_btn',function () {
    if(check_authenticated() === false){
        return;
    }
    let amount = balanceInput.val()
    balanceInput.val('')
    if (Number(amount) === 0){
        return
    }
    balance_socket.send(JSON.stringify(
        {
            'status' : $(this).hasClass('plus_btn') ? 'plus':'minus',
            'amount' : amount,
        }
    ))

})
// ACCOUNT AUDIT
let progressBar = $('.progress-bar')
let audit_running = false
let audit_socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/audit/'
);
$('.audit_btn').on('click',function () {
    if(check_authenticated() === false){
        return;
    }
    // if(audit_running){
    //     Swal.fire({
    //       position: 'center',
    //       icon: 'error',
    //       title: 'Ждём окончания аудита',
    //       showConfirmButton: false,
    //       timer: 1500
    //     })
    //     return;
    // }
    // audit_running=true
    audit_socket.send(JSON.stringify(
        {}
    ))
})
audit_socket.onmessage = (e) => {
    let percent = parseInt(JSON.parse(e.data)['percent'],10);
    let status = JSON.parse(e.data)['status'];
    if(status===false){
        Swal.fire({
          position: 'center',
          icon: 'error',
          title: 'Ждём окончания аудита',
          showConfirmButton: false,
          timer: 1500
        })
        return;
    }
    progressBar.width(percent + "%").attr('aria-valuenow',percent);
    progressBar.html(percent + "%")
    if(percent===100){
        Swal.fire({
          position: 'center',
          icon: 'success',
          title: 'Бухгалтерский аудит успешно завершён',
          showConfirmButton: false,
          timer: 1500
        })
        progressBar.width(0 + "%").attr('aria-valuenow',0)
        // audit_running=false

    }
}
audit_socket.onclose = (e) => {
    console.log("Audit socket closed!");
}

//Fruit store
let storeInput = $('.store_input')
storeInput.bind('keyup', function(e) {
    if(this.value < 1 || Number(this.value) === 0){
        this.value= ''
    }
});
let tradingBtn = $('.trading_btn')
let store_socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/store/'
);
tradingBtn.on('click','.btn_buy, .btn_sell',function () {
    if(check_authenticated() === false){
        return;
    }
    let storeInput = $(this).parent().find('.store_input')
    let amount = storeInput.val()
    storeInput.val('')
    if (Number(amount) === 0){
        return
    }
    let id = storeInput.data('id')
    store_socket.send(JSON.stringify(
        {
            'status' : $(this).hasClass('btn_buy') ? 'buy':'sell',
            'crontab': false,
            'id' : id,
            'amount' : amount,
        }
    ))
})
store_socket.onmessage = (e) => {
    let id = JSON.parse(e.data)['operation']['fruit_id']
    let crontab = JSON.parse(e.data)['crontab']
    let operation_count = JSON.parse(e.data)['count']
    $('.uploaded_count').html(operation_count)
    let timestamp = JSON.parse(e.data)['operation']['timestamp']
    let message = JSON.parse(e.data)['operation']['message']
    let status = JSON.parse(e.data)['operation']['status']
    let storeInput = $(`[data-id=${id}]`)
    let full_message = timestamp+' - '+message;
    storeInput.parents('.fruit').find('.fruit_last_operation').html(full_message)
    let newElement = $(`
        <div  class="direct-chat-msg ${ status==='SUCCESS' ? "bg-success" : "bg-danger"  } border p-2 rounded-3" >
            <div class="direct-chat-infos clearfix">
                <span class="direct-chat-name float-left">${status}</span>
                <span class="direct-chat-timestamp float-right text-white">${timestamp}</span>
            </div>
            <div class="">
                ${message}
            </div>
        </div>
    `)
    $('.last_operations').prepend(newElement)
    if (status === 'ERROR'){
        if(crontab === false) {
            toastr.error(`${full_message}`)
        }
        return
    }
    let balance = JSON.parse(e.data)['balance'];
    $(".balance_view").html(balance)
    let amount = JSON.parse(e.data)['amount'];
    storeInput.parents('.fruit').find('.fruit_amount').html(amount)
    if(crontab === false) {
        toastr.success(`${full_message}`)
    }
}
store_socket.onclose = (e) => {
    console.log("Store socket closed!");
}
// Declaration
let declarationBtn = $('.declaration_btn')
let declarationForm = $('.declaration_form')
let declarationFile = $('.declaration_file')
declarationBtn.on('click',function () {
    declarationFile.click()
})
declarationFile.on('change',function () {
    const formData = new FormData(declarationForm[0]);
    $.ajax({
    headers: { "X-CSRFToken": $.cookie("csrftoken") },
    url: '/admin/upload-declaration',
    method: 'post',
    data: formData,
    processData: false,
    contentType: false,
      success: function(response) {
        response = JSON.parse(response)
        try {
          var count = jQuery.parseJSON(response['count']);
        } catch (e) {
          // Error occurred during parse, consider it undefined
          console.log('JSON parse undefined:', e);
        }
       $('.uploaded_count').html(count)
      },
      error: function(xhr, status, error) {
        console.error('Declaration error');
        console.error('Error:', error);
      }
    });
})