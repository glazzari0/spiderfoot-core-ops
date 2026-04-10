activeTab = "global";
function saveSettings() {
    var retarr = {}
    $(":input").each(function(i) {
        retarr[$(this).attr('id')] = $(this).val();
    });

    $("#allopts").val(JSON.stringify(retarr));
}

function clearSettings() {
    $("#allopts").val("RESET");
}

function switchTab(tab) {
    $("#optsect_"+activeTab).hide();
    $("#optsect_"+tab).show();
    $("#tab_"+activeTab).removeClass("active");
    $("#tab_"+tab).addClass("active");
    activeTab = tab;
}

function getRequestedModuleTab() {
    var requestedModule = window.preselectedModule || null;
    var params = new URLSearchParams(window.location.search);

    if (!requestedModule) {
        requestedModule = params.get("module");
    }

    if (!requestedModule && window.location.hash) {
        requestedModule = window.location.hash.replace(/^#/, "");
    }

    if (!requestedModule) {
        return null;
    }

    if ($("#tab_" + requestedModule).length === 0 || $("#optsect_" + requestedModule).length === 0) {
        return null;
    }

    return requestedModule;
}

function getFile(elemId) {
   var elem = document.getElementById(elemId);
   if(elem && document.createEvent) {
      var evt = document.createEvent("MouseEvents");
      evt.initEvent("click", true, false);
      elem.dispatchEvent(evt);
   }
}

$(document).ready(function() {
  $("#btn-save-changes").click(function() { saveSettings(); });
  $("#btn-import-config").click(function() { getFile("configFile"); return false; });
  $("#btn-reset-settings").click(function() { clearSettings(); });
  $("#btn-opt-export").click(function() { window.location.href=docroot + "/optsexport?pattern=api_key"; return false; });
  $("#tab_global").click(function() { switchTab("global"); });

  var requestedModule = getRequestedModuleTab();
  if (requestedModule) {
      switchTab(requestedModule);
  }
});

$(function () {
  $('[data-toggle="popover"]').popover()
  $('[data-toggle="popover"]').on("show.bs.popover", function() { $(this).data("bs.popover").tip().css("max-width", "600px") });
});
