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

function renderOllamaModels(data) {
    var allModels = data.models || [];
    var chatModels = data.chat_models || [];
    var embeddingModels = data.embedding_models || [];
    var options = "";

    allModels.forEach(function(name) {
        options += "<option value=\"" + $("<div>").text(name).html() + "\"></option>";
    });
    $("#ai-ollama-models").html(options);

    if (!$("#_ai_ollama_chat_model").val() && chatModels.length > 0) {
        $("#_ai_ollama_chat_model").val(chatModels[0]);
    }
    if (!$("#_ai_ollama_embedding_model").val() && embeddingModels.length > 0) {
        $("#_ai_ollama_embedding_model").val(embeddingModels[0]);
    }

    var summary = "";
    if (chatModels.length > 0) {
        summary += "<div><b>Modelos de chat:</b> " + chatModels.map(function(name) { return $("<div>").text(name).html(); }).join(", ") + "</div>";
    }
    if (embeddingModels.length > 0) {
        summary += "<div><b>Modelos de embeddings:</b> " + embeddingModels.map(function(name) { return $("<div>").text(name).html(); }).join(", ") + "</div>";
    }
    if (!summary) {
        summary = "<div>Nenhum modelo retornado pelo Ollama.</div>";
    }
    $("#ai-ollama-model-summary").html(summary);
}

function testOllamaConnection() {
    var baseUrl = ($("#_ai_ollama_base_url").val() || "").trim();
    if (!baseUrl) {
        $("#ai-ollama-status").removeClass("text-success").addClass("text-danger").text("Informe a URL do servidor Ollama antes de validar.");
        return false;
    }

    $("#ai-ollama-status").removeClass("text-danger text-success").addClass("text-muted").text("Consultando o servidor Ollama e carregando os modelos disponíveis...");
    $("#ai-ollama-model-summary").html("");

    $.ajax({
        type: "POST",
        url: docroot + "/aiollamamodels",
        data: { base_url: baseUrl },
        cache: false,
        dataType: "json"
    }).done(function(data) {
        $("#ai-ollama-status").removeClass("text-danger text-muted").addClass("text-success").text(data.message || "Conexão com Ollama validada.");
        renderOllamaModels(data);
    }).fail(function(hr, status) {
        var message = "Falha ao consultar o Ollama.";
        if (hr.responseJSON && hr.responseJSON.error && hr.responseJSON.error.message) {
            message = hr.responseJSON.error.message;
        } else if (hr.responseText) {
            message = hr.responseText;
        } else if (status) {
            message = status;
        }
        $("#ai-ollama-status").removeClass("text-success text-muted").addClass("text-danger").text(message);
        $("#ai-ollama-model-summary").html("");
    });

    return false;
}

$(document).ready(function() {
  $("#btn-save-changes").click(function() { saveSettings(); });
  $("#btn-import-config").click(function() { getFile("configFile"); return false; });
  $("#btn-reset-settings").click(function() { clearSettings(); });
  $("#btn-opt-export").click(function() { window.location.href=docroot + "/optsexport?pattern=api_key"; return false; });
  $("#tab_global").click(function() { switchTab("global"); });
  $("#tab_ai").click(function() { switchTab("ai"); });
  $("#btn-ai-test-ollama").click(function() { return testOllamaConnection(); });

  var requestedModule = getRequestedModuleTab();
  if (requestedModule) {
      switchTab(requestedModule);
  }
});

$(function () {
  $('[data-toggle="popover"]').popover()
  $('[data-toggle="popover"]').on("show.bs.popover", function() { $(this).data("bs.popover").tip().css("max-width", "600px") });
});
