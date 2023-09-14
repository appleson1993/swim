

function cancelRequest(id) {

  fetch('/api/cancel?id='+id)
    .then(response => {
      //把fetch結果alert出來

        console.log(response.text());
    })
    .catch(error => {
        console.log(response.text());
        alert("取消失敗");
    });
swal.close();

}