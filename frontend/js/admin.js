function renderTable(data) {
  let table = $('#table-summary');
  
  for(let i=0; i<data.length; i++) {
    table.append('<tr><td>'+ (i+1) +'</td><td>'+data[i].word +'</td><td>'+ data[i].count +'</td></tr>');  
  }
}

function getData() {
  $.ajax({
    method: 'GET',
    url: "words",
    success: function(result){
      renderTable(result);
    }
  });
}

$(function() {
  getData();
});
