function poptastic(url) {
      var w = 450;
      var h = 600;
      var left = (screen.width/2)-(w/2);
      var top = (screen.height/2)-(h/2);
      var newWindow = window.open(url, 'Login', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
     if (window.focus) {
        newWindow.focus();
      }
    };

$(document).ready(function() {

  $(function() {  
    var window_height = $(window).height(),
    content_height = window_height - 340;
    $('.scroll-table').height(content_height);
  });

  $( window ).resize(function() {
    var window_height = $(window).height(),
    content_height = window_height - 340;
    $('.scroll-table').height(content_height);
  });

  var show_alert = function(alert_type, alert_message) {  
    var alerts = "alert-info alert-success alert-danger aler-warning";
    $("#alert-box").removeClass(alerts);
    $("#alert-box").addClass(alert_type);
    $("#alert-message").html(alert_message);
    $("#alert-box").addClass('in');
    setTimeout(function() {$("#alert-box").removeClass('in');}, 5000);
  };

  $(function() {
    var i = $("#info").attr("info");
    switch (i) {
      case '1': show_alert("alert-success", "new bill is added"); break;
      case '2': show_alert("alert-danger", "some payment methods used are no longer available"); break;
      case '3': show_alert("alert-success", "all bills in the event are deleted"); break;
      case '4': show_alert("alert-success", "changes of payment methods are saved"); break; 
      case '5': show_alert("alert-info", "payment methods not changed"); break;
      case '6': show_alert("alert-danger", "no bill in the event"); break;
      case '7': show_alert("alert-success", "new event is added"); break;
      case '8': show_alert("alert-success", "chosen event is deleted"); break;
      case '9': show_alert("alert-info", "no further transcation needed"); break;
      case '10': show_alert("alert-danger", "did not find any solution"); break;
    }
  });

  $("#event").tooltip();
  $("#add-icon").tooltip();
  $(".delete-icon").tooltip();
/*
  $(".save-icon").tooltip();
  $(".cancel-icon").tooltip();
*/
  $(".back-icon").tooltip();
  $(".balance-icon").tooltip();
  $(".graph-icon").tooltip();

  $(".record-row").hover(
    function() {
      $(this).find(".delete-icon").html("<span class='glyphicon glyphicon-minus-sign text-muted'></span>");
      $(this).find(".modify-icon").html("<span class='glyphicon glyphicon-pencil text-muted'></span>");
    }, function() {
      $(this).find(".delete-icon").html("");
      $(this).find(".modify-icon").html("");
    }
  );


  $(".add-record").click(
    function() {
      $("#addicon-row").hide();
      /* $("#add-row").css("visibility", "visible"); */
      $(".scroll-table").animate({scrollTop: $(".scroll-table")[0].scrollHeight}, 'slow');
      $("#add-row").fadeIn();
      if ($("#input-name").val() == "") {
        $("#input-name").focus();
      } else {
        $("#input-amount").focus();
      }
    }
  );

  $(".back-icon").click(
    function() {
      eventname = $("#eventname").html();
      window.location.href = "/?event=" + eventname;
    }
  );

  $(".close-btn").hover(
    function() {
      $(this).css({"color": "#aaaaaa"});
    }, function() {
      $(this).css({"color": "#ffffff"});
    }
  );

  $(".close-btn").click(
    function() {
      $('#method_' + $(this).parent().attr('id')).html('');
      $(this).parent().fadeOut();
    }
  );

  $(".method-close-btn").click(
    function() {
      var method_name = $(this).parent().attr('id').replace("method-","");
      var methods = $("#edit-payment-methods").val();
      methods = methods.replace("[" + method_name + "]", "");
      $("#edit-payment-methods").val(methods);
      $(this).parent().fadeOut();
    }
  );

  $("#form-add").submit(
    function() {
      if ($("#input-name").val() == '') {
        show_alert("alert-danger", "name is missing");
        $("#input-name").focus();
        return false;
      }
      if ($("#input-amount").val() == '') {
        show_alert("alert-danger", "amount of money is missing");
        $("#input-amount").focus();
        return false;
      } else if (isNaN($("#input-amount").val())) {
        show_alert("alert-danger", "invaild amount of money");
        $("#input-amount").val('');
        $("#input-amount").focus();
        return false;
      }
    }
  );

  $("#close-alert").click(
    function() {
      $("#alert-box").removeClass('in');
    }
  );

  $("#delete-event").click(
    function() {
      bootbox.confirm("delete the current event for sure?", function(result) {
        if (result == true ) {
          window.location.href = "/delete_event?name=" + $("#eventname").html();
        }
      });
    }
  );

  $("#delete-records").click(
    function() {
      bootbox.confirm("delete all bills in this event for sure?", function(result) {
        if (result == true ) {
          window.location.href = "/delete_records?event=" + $("#eventname").html();
        }
      });
    }
  );

  $("#new-event").click(
    function() {
      bootbox.prompt("new event name", function(result) {
        if (result === null) {
        } else if (result == "") {
          show_alert("alert-danger", "new event name is missing");
        } else {
          if ($("#event_" + result).length > 0) {
            show_alert("alert-danger", "event name already exists");
          } else {
            window.location.href = "/add_event?name=" + result.toUpperCase();
          }
        }
      });
    }
  );

  $("#edit-methods-btn").click(
    function() {
      window.location.href = "/methods?event=" + $("#eventname").html() + "&methods=" + $("#input-methods").val();
    }
  );

  $(".view-result").click(
    function() {
      $("#calculate").submit();
    }
  );

  $(".view-balances").click(
    function() {
      $("#show").val("balances");
      $("#calculate").submit();
    }
  );

  $(".save-icon").click(
    function() {
      $("#form-add").submit();
    }
  );

  $(".cancel-icon").click(
    function() {
      $("#addicon-row").fadeIn();
      $("#add-row").hide();
      $("#input-name").val($("#username").children().html());
      $("#input-amount").val('');
      $("#input-note").val('');
    }
  );

  $(".save-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );

  $(".cancel-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );

  $(".hover-larger").hover(
    function() {
      $(this).addClass('big');
    }, function() {
      $(this).removeClass('big');
    }
  );

  $(".back-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );

  $(".balance-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );

  $(".graph-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );

  $(".table-icon").hover(
    function() {
      $(this).removeClass('text-muted');
      $(this).addClass('text-primary');
    }, function() {
      $(this).removeClass('text-primary');
      $(this).addClass('text-muted');
    }
  );


  $("#calculate").submit(
    function() {
      if ($("#tolerance").val() == '') {
        show_alert("alert-danger", "tolerance is missing");
        $("#tolerance").focus();
        return false;
      } else if (isNaN($("#tolerance").val())) {
        show_alert("alert-danger", "invaild tolerance");
        $("#tolerance").val('');
        $("#tolerance").focus();
        return false;
      }
    } 
  );

   $(".delete-icon").click(
    function() {
      var delete_url = $(this).attr('url');
      bootbox.confirm("delete this bill for sure?", function(result) {
        if (result == true ) {
          window.location.href = delete_url;
        }
      });
    }
  );

  $("#graph-icon").click(
    function() {
      $("#payment-table").toggle('slide');
      $("#payment-graph").toggle('slide');
      if ($("#view-payments").html() == 'view payments graph') {
        $("#view-payments").html('view payments table');
      } else {
        $("#view-payments").html('view payments graph');
      }

    }
  );

  $("#table-icon").click(
    function() {
      $("#payment-graph").toggle('slide');
      $("#payment-table").toggle('slide');
      if ($("#view-payments").html() == 'view payments graph') {
        $("#view-payments").html('view payments table');
      } else {
        $("#view-payments").html('view payments graph');
      }

    }
  );

  $("#view-payments").click(
    function() {
      $("#payment-table").toggle('slide');
      $("#payment-graph").toggle('slide');
      if ($(this).html() == 'view payments graph') {
        $(this).html('view payments table');
      } else {
        $(this).html('view payments graph');
      }
    }
  );


});
