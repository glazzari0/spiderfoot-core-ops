var geoipRows = [];

function geoipSetLoading(loading) {
    if (loading) {
        $("#geoip-loader").show();
    } else {
        $("#geoip-loader").fadeOut(300);
    }
}

function geoipFillSelect(selectId, files, selectedValue) {
    var select = $(selectId);
    select.empty();
    select.append("<option value=''>-- none --</option>");
    for (var i = 0; i < files.length; i++) {
        var option = $("<option></option>")
            .attr("value", files[i].path)
            .text(files[i].label);
        if (selectedValue && selectedValue === files[i].path) {
            option.prop("selected", true);
        }
        select.append(option);
    }
}

function geoipLoadDatasets() {
    geoipSetLoading(true);
    sf.fetchData(docroot + "/geoipdatasets", null, function(data) {
        geoipSetLoading(false);
        if (data.error) {
            alertify.error(data.error.message);
            return;
        }

        geoipFillSelect("#geoip-city-blocks-file", data.datasets.city_blocks || [], data.defaults.city_blocks);
        geoipFillSelect("#geoip-asn-blocks-file", data.datasets.asn_blocks || [], data.defaults.asn_blocks);
        geoipFillSelect("#geoip-city-locations-file", data.datasets.city_locations || [], data.defaults.city_locations);
        geoipFillSelect("#geoip-country-locations-file", data.datasets.country_locations || [], data.defaults.country_locations);
    });
}

function geoipCollectPreviewRequest() {
    return {
        city_blocks_file: $("#geoip-city-blocks-file").val(),
        asn_blocks_file: $("#geoip-asn-blocks-file").val(),
        city_locations_file: $("#geoip-city-locations-file").val(),
        country_locations_file: $("#geoip-country-locations-file").val(),
        network_filter: $("#geoip-network-filter").val(),
        asn_filter: $("#geoip-asn-filter").val(),
        organization_filter: $("#geoip-org-filter").val(),
        city_filter: $("#geoip-city-filter").val(),
        country_filter: $("#geoip-country-filter").val(),
        limit: $("#geoip-limit").val()
    };
}

function geoipHasMeaningfulFilter(request) {
    return Boolean(
        (request.network_filter || "").trim() ||
        (request.asn_filter || "").trim() ||
        (request.organization_filter || "").trim() ||
        (request.city_filter || "").trim() ||
        (request.country_filter || "").trim()
    );
}

function geoipRenderTable(rows) {
    if (!rows || rows.length === 0) {
        $("#geoip-table-container").html("<div class='alert alert-warning'>Nenhuma rede encontrada com os filtros informados.</div>");
        return;
    }

    var defaultPageSize = rows.length < 25 ? rows.length : 25;
    if (defaultPageSize <= 0) {
        defaultPageSize = 10;
    }

    var html = "";
    html += "<div class='table-responsive'>";
    html += "<table id='geoip-table' class='table table-bordered table-striped tablesorter'>";
    html += "<thead><tr>";
    html += "<th class='text-center'><input id='geoip-checkall' type='checkbox'></th>";
    html += "<th>Rede</th><th>IPs</th><th>ASN</th><th>Organização</th><th>País</th><th>UF</th><th>Cidade</th><th>Geoname</th>";
    html += "</tr></thead><tbody>";

    for (var i = 0; i < rows.length; i++) {
        html += "<tr>";
        html += "<td class='text-center'><input class='geoip-row-check' type='checkbox' data-index='" + i + "'></td>";
        html += "<td>" + rows[i].network + "</td>";
        html += "<td class='text-center'>" + rows[i].num_addresses + "</td>";
        html += "<td>" + (rows[i].asn || "") + "</td>";
        html += "<td>" + (rows[i].organization || "") + "</td>";
        html += "<td>" + ((rows[i].country_name || "") + " " + (rows[i].country_iso_code || "")).trim() + "</td>";
        html += "<td>" + (rows[i].subdivision_1_name || "") + "</td>";
        html += "<td>" + (rows[i].city_name || "") + "</td>";
        html += "<td>" + (rows[i].geoname_id || "") + "</td>";
        html += "</tr>";
    }

    html += "</tbody></table>";
    html += "</div>";
    html += "<div id='geoip-pager' class='pager'>";
    html += "<form>";
    html += "<button type='button' class='first btn btn-default btn-sm'>Primeira</button>";
    html += "<button type='button' class='prev btn btn-default btn-sm'>Anterior</button>";
    html += "<span class='pagedisplay'></span>";
    html += "<button type='button' class='next btn btn-default btn-sm'>Próxima</button>";
    html += "<button type='button' class='last btn btn-default btn-sm'>Última</button>";
    html += "<select class='pagesize form-control' style='display:inline-block; width:auto; margin-left:10px;'>";
    html += "<option" + (defaultPageSize === 10 ? " selected='selected'" : "") + " value='10'>10</option>";
    html += "<option" + (defaultPageSize === 25 ? " selected='selected'" : "") + " value='25'>25</option>";
    html += "<option" + (defaultPageSize === 50 ? " selected='selected'" : "") + " value='50'>50</option>";
    html += "<option" + (defaultPageSize === 100 ? " selected='selected'" : "") + " value='100'>100</option>";
    html += "<option value='250'>250</option>";
    html += "<option value='500'>500</option>";
    html += "<option value='1000'>1000</option>";
    html += "<option value='" + rows.length + "'>Todos</option>";
    html += "</select>";
    html += "</form>";
    html += "</div>";
    $("#geoip-table-container").html(html);

    $("#geoip-checkall").on("change", function() {
        $(".geoip-row-check").prop("checked", this.checked);
    });

    $("#geoip-table").tablesorter({
        headers: {
            0: { sorter: false }
        }
    }).tablesorterPager({
        container: $("#geoip-pager"),
        size: defaultPageSize,
        output: "{startRow} - {endRow} / {totalRows}"
    });
}

function geoipPreview() {
    var request = geoipCollectPreviewRequest();
    if (!request.city_locations_file) {
        alertify.message("Selecione o arquivo City Locations.");
        return;
    }
    if (!request.country_locations_file) {
        alertify.message("Selecione o arquivo Country Locations.");
        return;
    }
    if (!request.asn_blocks_file) {
        alertify.message("Selecione o arquivo ASN Blocks IPv4.");
        return;
    }
    if (!geoipHasMeaningfulFilter(request)) {
        alertify.message("Informe pelo menos um filtro antes de expandir as networks.");
        return;
    }
    if (!request.city_blocks_file) {
        alertify.message("Selecione o arquivo de blocos City Blocks IPv4 para expandir as networks filtradas.");
        return;
    }

    geoipSetLoading(true);
    sf.fetchData(docroot + "/geoippreview", request, function(data) {
        geoipSetLoading(false);
        if (data.error) {
            alertify.error(data.error.message);
            return;
        }

        geoipRows = data.rows || [];
        geoipRenderTable(geoipRows);

        var summary = "Total no arquivo: " + data.total_rows + " | Correspondências: " + data.matched_rows + " | Exibidas: " + data.returned_rows;
        if (data.truncated) {
            summary += " | Resultado truncado pelo limite";
        }
        $("#geoip-preview-summary").text(summary);
    });
}

function geoipGetSelections() {
    var selections = [];
    $(".geoip-row-check:checked").each(function() {
        var index = parseInt($(this).attr("data-index"), 10);
        if (!isNaN(index) && geoipRows[index]) {
            selections.push(geoipRows[index]);
        }
    });
    return selections;
}

function geoipStartScans() {
    var selections = geoipGetSelections();
    if (selections.length === 0) {
        alertify.message("Selecione pelo menos uma rede.");
        return;
    }

    geoipSetLoading(true);
    sf.fetchData(docroot + "/geoipstartscans", {
        selections: JSON.stringify(selections),
        usecase: $("#geoip-usecase").val(),
        max_ips_per_network: $("#geoip-max-ips-per-network").val(),
        max_scans: $("#geoip-max-scans").val(),
        usable_hosts_only: $("#geoip-usable-hosts-only").is(":checked") ? "1" : "0",
        name_template: $("#geoip-name-template").val()
    }, function(data) {
        geoipSetLoading(false);
        if (data.error) {
            alertify.error(data.error.message);
            return;
        }

        var summary = "Varreduras criadas: " + data.created_count + " | Falhas: " + data.failed_count;
        if (data.created_count > 0) {
            summary += " | Veja a aba Varreduras para acompanhar.";
            alertify.success(summary);
        } else {
            alertify.warning(summary);
        }
        $("#geoip-start-summary").text(summary);
    });
}

$(document).ready(function() {
    geoipLoadDatasets();

    $("#geoip-preview-button").on("click", geoipPreview);
    $("#geoip-start-button").on("click", geoipStartScans);
    $("#geoip-select-all-button").on("click", function() {
        $(".geoip-row-check").prop("checked", true);
        $("#geoip-checkall").prop("checked", true);
    });
    $("#geoip-select-none-button").on("click", function() {
        $(".geoip-row-check").prop("checked", false);
        $("#geoip-checkall").prop("checked", false);
    });
});
