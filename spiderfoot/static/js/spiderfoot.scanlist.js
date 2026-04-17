globalTypes = null;
globalFilter = null;
globalScanData = [];
lastChecked = null;

function switchSelectAll() {
    if (!$("#checkall")[0].checked) {
        $("input[id*=cb_]").prop('checked', false);
    } else {
        $("input[id*=cb_]").prop('checked', true);
    }
}

function filter(type) {
    if (type == "all") {
        showlist();
        return;
    }
    if (type == "running") {
        showlist(["RUNNING", "STARTING", "STARTED", "INITIALIZING"], "Em execuÃ§Ã£o");
        return;
    }
    if (type == "finished") {
        showlist(["FINISHED"], "ConcluÃ­das");
        return;
    }
    if (type == "failed") {
        showlist(["ABORTED", "FAILED"], "Falhas/Abortadas");
        return;
    }
}

function getSelected() {
    ids = [];
    $("input[id*=cb_]").each(function(i, obj) {
        if (obj.checked) {
            ids[ids.length] = obj.id.replace("cb_", "");
        }
    });

    if (ids.length == 0)
        return false;

    return ids;
}

function stopScan(id) {
    alertify.confirm("Tem certeza de que deseja parar esta varredura?",
    function(){
        sf.stopScan(id, reload);
    }).set({title:"Parar varredura?"});
}

function stopSelected() {
    ids = getSelected();
    if (!ids) {
        alertify.message("NÃ£o foi possÃ­vel parar as varreduras. Nenhuma varredura foi selecionada.");
        return;
    }

    alertify.confirm("Tem certeza de que deseja parar estas " + ids.length + " varreduras?<br/><br/>" + ids.join("<br/>"),
    function(){
        sf.stopScan(ids.join(','), reload);
    }).set({title:"Parar varreduras?"});
}

function deleteScan(id) {
    alertify.confirm("Tem certeza de que deseja excluir esta varredura?",
    function(){
        sf.deleteScan(id, removeDeletedScansFromView);
    }).set({title:"Excluir varredura?"});
}

function deleteSelected() {
    ids = getSelected();
    if (!ids) {
        alertify.message("NÃ£o foi possÃ­vel excluir as varreduras. Nenhuma varredura foi selecionada.");
        return;
    }

    alertify.confirm("Tem certeza de que deseja excluir estas " + ids.length + " varreduras?<br/><br/>" + ids.join("<br/>"),
    function(){
        sf.deleteScan(ids.join(','), removeDeletedScansFromView);
    }).set({title:"Excluir varreduras?"});
}

function rerunSelected() {
    ids = getSelected();
    if (!ids) {
        alertify.message("NÃ£o foi possÃ­vel executar novamente. Nenhuma varredura foi selecionada.");
        return;
    }

    sf.log("Executando novamente as varreduras: " + ids.join(','));
    window.location.href = docroot + '/rerunscanmulti?ids=' + ids.join(',');
}

function exportSelected(type) {
    ids = getSelected();

    if (!ids) {
        sf.log("Erro: nenhuma varredura selecionada");
        return;
    }

    $("#loader").show();
    var efr = document.getElementById('exportframe');
    switch(type) {
        case "gexf":
            sf.log("Exportando varreduras como " + type + ": " + ids.join(','));
            efr.src = docroot + '/scanvizmulti?ids=' + ids.join(',');
            break;
        case "csv":
            sf.log("Exportando varreduras como " + type + ": " + ids.join(','));
            efr.src = docroot + '/scaneventresultexportmulti?ids=' + ids.join(',');
            break;
        case "excel":
            sf.log("Exportando varreduras como " + type + ": " + ids.join(','));
            efr.src = docroot + '/scaneventresultexportmulti?filetype=excel&ids=' + ids.join(',');
            break;
        case "json":
            sf.log("Exportando varreduras como " + type + ": " + ids.join(','));
            efr.src = docroot + '/scanexportjsonmulti?ids=' + ids.join(',');
            break;
        default:
            sf.log("Erro: tipo de exportaÃ§Ã£o invÃ¡lido: " + type);
    }
    $("#loader").fadeOut(500);
}

function reload() {
    $("#loader").show();
    showlist(globalTypes, globalFilter);
    return;
}

function renderEmptyScanState() {
    $("#loader").fadeOut(500);
    $("#scancontent-wrapper").remove();
    $("#scancontent .scanlist-empty-state").remove();
    welcome = "<div class='alert alert-info scanlist-empty-state'>";
        welcome += "<h4>Nenhum hist&#243;rico de varreduras</h4><br>";
        welcome += "No momento n&#227;o h&#225; hist&#243;rico de varreduras executadas. Clique em 'Nova Varredura' para iniciar uma nova an&#225;lise.";
    welcome += "</div>";
    $("#scancontent").append(welcome);
}

function removeDeletedScansFromView(deletedIds) {
    var ids = deletedIds || [];
    if (!ids.length) {
        reload();
        return;
    }

    globalScanData = (globalScanData || []).filter(function(item) {
        return $.inArray(item[0], ids) === -1;
    });

    if (!globalScanData.length) {
        renderEmptyScanState();
        return;
    }

    showlisttable(globalTypes, globalFilter, globalScanData);
}

function showlist(types, filter) {
    globalTypes = types;
    globalFilter = filter;
    sf.fetchData(docroot + '/scanlist', null, function(data) {
        globalScanData = data || [];
        if (data.length == 0) {
            renderEmptyScanState();
            return;
        }

        showlisttable(types, filter, data)
    });
}

function showlisttable(types, filter, data) {
    if (filter == null) {
        filter = "Nenhum";
    }
    var buttons = "<div class='btn-toolbar sf-toolbar scanlist-toolbar'>";
    buttons += "<div class='btn-group'>";
    buttons += "<button id='btn-filter' class='btn btn-default'><i class='glyphicon glyphicon-filter'></i>&nbsp;Filtro: " + filter + "</button>";
    buttons += "<button class='btn dropdown-toggle btn-default' data-toggle='dropdown'><span class='caret'></span></button>";
    buttons += "<ul class='dropdown-menu'>";
    buttons += "<li><a href='javascript:filter(\"all\")'>Nenhum</a></li>";
    buttons += "<li><a href='javascript:filter(\"running\")'>Em execuÃ§Ã£o</a></li>";
    buttons += "<li><a href='javascript:filter(\"finished\")'>ConcluÃ­das</a></li>";
    buttons += "<li><a href='javascript:filter(\"failed\")'>Falhas/Abortadas</a></li></ul>";
    buttons += "</div>";

    buttons += "<div class='btn-group pull-right'>";
    buttons += "<button rel='tooltip' data-title='Excluir Selecionadas' id='btn-delete' class='btn btn-default btn-danger'><i class='glyphicon glyphicon-trash glyphicon-white'></i></button>";
    buttons += "</div>";

    buttons += "<div class='btn-group pull-right'>";
    buttons += "<button rel='tooltip' data-title='Atualizar' id='btn-refresh' class='btn btn-default btn-success'><i class='glyphicon glyphicon-refresh glyphicon-white'></i></a>";
    buttons += "<button rel='tooltip' data-toggle='dropdown' data-title='Exportar Selecionadas' id='btn-export' class='btn btn-default btn-success dropdown-toggle download-button'><i class='glyphicon glyphicon-download-alt glyphicon-white'></i></button>";
    buttons += "<ul class='dropdown-menu'>";
    buttons += "<li><a href='javascript:exportSelected(\"csv\")'>CSV</a></li>";
    buttons += "<li><a href='javascript:exportSelected(\"excel\")'>Excel</a></li>";
    buttons += "<li><a href='javascript:exportSelected(\"gexf\")'>GEXF</a></li>";
    buttons += "<li><a href='javascript:exportSelected(\"json\")'>JSON</a></li>";
    buttons += "</ul>";
    buttons += "</div>";

    buttons += "<div class='btn-group pull-right'>";
    buttons += "<button rel='tooltip' data-title='Executar Novamente Selecionadas' id='btn-rerun' class='btn btn-default'><i class='glyphicon glyphicon-repeat glyphicon-white'></i></button>";
    buttons += "<button rel='tooltip' data-title='Parar Selecionadas' id='btn-stop' class='btn btn-default'>";
    buttons += "<i class='glyphicon glyphicon-stop glyphicon-white'></i></button>";
    buttons += "</div>";

    buttons += "</div>";
    var table = "<div class='sf-table-shell scanlist-shell'><table id='scanlist' class='table table-striped scanlist-table'>";
    table += "<thead><tr><th class='sorter-false text-center'><input id='checkall' type='checkbox'></th> <th>Nome</th> <th>Alvo</th> <th>InÃ­cio</th> <th >Fim</th> <th class='text-center'>Status</th> <th class='text-center'>Elementos</th><th class='text-center'>CorrelaÃ§Ãµes</th><th class='sorter-false text-center'>AÃ§Ã£o</th> </tr></thead><tbody>";
    filtered = 0;
    for (var i = 0; i < data.length; i++) {
        if (types != null && $.inArray(data[i][6], types)) {
            filtered++;
            continue;
        }
        table += "<tr><td class='text-center'><input type='checkbox' id='cb_" + data[i][0] + "'></td>"
        table += "<td><a href=" + docroot + "/scaninfo?id=" + data[i][0] + ">" + data[i][1] + "</a></td>";
        table += "<td>" + data[i][2] + "</td>";
        table += "<td>" + data[i][3] + "</td>";
        table += "<td>" + data[i][5] + "</td>";

        var statusy = "";

        if (data[i][6] == "FINISHED") {
            statusy = "alert-success";
        } else if (data[i][6].indexOf("ABORT") >= 0) {
            statusy = "alert-warning";
        } else if (data[i][6] == "CREATED" || data[i][6] == "RUNNING" || data[i][6] == "STARTED" || data[i][6] == "STARTING" || data[i][6] == "INITIALIZING") {
            statusy = "alert-info";
        } else if (data[i][6].indexOf("FAILED") >= 0) {
            statusy = "alert-danger";
        } else {
            statusy = "alert-info";
        }
        table += "<td class='text-center'><span class='badge " + statusy + "'>" + data[i][6] + "</span></td>";
        table += "<td class='text-center'>" + data[i][7] + "</td>";
        table += "<td class='text-center'>";
        table += "<span class='badge alert-danger'>" + data[i][8]['HIGH'] + "</span>";
        table += "<span class='badge alert-warning'>" + data[i][8]['MEDIUM'] + "</span>";
        table += "<span class='badge alert-info'>" + data[i][8]['LOW'] + "</span>";
        table += "<span class='badge alert-success'>" + data[i][8]['INFO'] + "</span>";
        table += "</td>";
        table += "<td class='text-center'>";
        if (data[i][6] == "RUNNING" || data[i][6] == "STARTING" || data[i][6] == "STARTED" || data[i][6] == "INITIALIZING") {
            table += "<a rel='tooltip' title='Parar Varredura' href='javascript:stopScan(\"" + data[i][0] + "\");'><i class='glyphicon glyphicon-stop text-muted'></i></a>";
        } else {
            table += "<a rel='tooltip' title='Excluir Varredura' href='javascript:deleteScan(\"" + data[i][0] + "\");'><i class='glyphicon glyphicon-trash text-muted'></i></a>";
            table += "&nbsp;&nbsp;<a rel='tooltip' title='Re-run Scan' href=" + docroot + "/rerunscan?id=" + data[i][0] + "><i class='glyphicon glyphicon-repeat text-muted'></i></a>";
        }
        table += "&nbsp;&nbsp;<a rel='tooltip' title='Clone Scan' href=" + docroot + "/clonescan?id=" + data[i][0] + "><i class='glyphicon glyphicon-plus-sign text-muted'></i></a>";
        table += "</td></tr>";
    }

    table += '</tbody><tfoot><tr><th colspan="8" class="ts-pager form-inline scanlist-pager">';
    table += '<div class="btn-group btn-group-sm" role="group">';
    table += '<button type="button" class="btn btn-default first"><span class="glyphicon glyphicon-step-backward"></span></button>';
    table += '<button type="button" class="btn btn-default prev"><span class="glyphicon glyphicon-backward"></span></button>';
    table += '</div>';
    table += '<div class="btn-group btn-group-sm" role="group">';
    table += '<button type="button" class="btn btn-default next"><span class="glyphicon glyphicon-forward"></span></button>';
    table += '<button type="button" class="btn btn-default last"><span class="glyphicon glyphicon-step-forward"></span></button>';
    table += '</div>';
    table += '<select class="form-control input-sm pagesize" title="Select page size">';
    table += '<option selected="selected" value="10">10</option>';
    table += '<option value="20">20</option>';
    table += '<option value="30">30</option>';
    table += '<option value="all">Todas as Linhas</option>';
    table += '</select>';
    table += '<select class="form-control input-sm pagenum" title="Select page number"></select>';
    table += '<span class="pagedisplay pull-right"></span>';
    table += '</th></tr></tfoot>';
    table += "</table></div>";

    $("#loader").fadeOut(500);
    $("#scancontent-wrapper").remove();
    $("#scancontent .scanlist-empty-state").remove();
    $("#scancontent").append("<div id='scancontent-wrapper'> " + buttons + table + "</div>");
    sf.updateTooltips();
    $("#scanlist").tablesorter().tablesorterPager({
      container: $(".ts-pager"),
      cssGoto: ".pagenum",
      output: 'Varreduras {startRow} - {endRow} / {filteredRows} ({totalRows})'
    });
    $("[class^=tooltip]").remove();

    $(document).ready(function() {
        var chkboxes = $('input[id*=cb_]');
        chkboxes.click(function(e) {
            if(!lastChecked) {
                lastChecked = this;
                return;
            }

            if(e.shiftKey) {
                var start = chkboxes.index(this);
                var end = chkboxes.index(lastChecked);

                chkboxes.slice(Math.min(start,end), Math.max(start,end)+ 1).prop('checked', lastChecked.checked);
            }

            lastChecked = this;
        });

        $("#btn-delete").click(function() { deleteSelected(); });
        $("#btn-refresh").click(function() { reload(); });
        $("#btn-rerun").click(function() { rerunSelected(); });
        $("#btn-stop").click(function() { stopSelected(); });
        $("#checkall").click(function() { switchSelectAll(); });
    });
}

showlist();
