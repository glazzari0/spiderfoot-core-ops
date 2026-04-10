    tabs = [ "use", "preset", "type", "module" ];
    activeTab = "use";

    function submitForm() {
        list = "";
        if (activeTab != "use" && activeTab != "preset") {
            $("[id^="+activeTab+"_]").each(function() {
                if ($(this).is(":checked")) {
                    list += $(this).attr('id') + ",";
                }
            });
        }

        if (activeTab == "type" || activeTab == "module") {
            $("#"+activeTab+"list").val(list);
        }

        if (activeTab != "preset") {
            $("input[name='preset']").prop("checked", false);
        }

        if (activeTab != "use") {
            $("input[name='usecase']").prop("checked", false);
        }

        for (i = 0; i < tabs.length; i++) {
            if (tabs[i] != activeTab) {
                if ($("#"+tabs[i]+"list").length) {
                    $("#"+tabs[i]+"list").val("");
                }
            }
        }
    }

    function switchTab(tabname) {
        $("#"+activeTab+"table").hide();
        $("#"+activeTab+"tab").removeClass("active");
        $("#"+tabname+"table").show();
        $("#"+tabname+"tab").addClass("active");
        activeTab = tabname;
        if (activeTab == "use" || activeTab == "preset") {
            $("#selectors").hide();
        } else {
            $("#selectors").show();
        }
    }

    function selectAll() {
        $("[id^="+activeTab+"_]").each(function() {
            if (!$(this).is(":disabled")) {
                $(this).prop("checked", true);
            }
        });
    }

    function deselectAll() {
        $("[id^="+activeTab+"_]").each(function() {
            if (!$(this).is(":disabled")) {
                $(this).prop("checked", false);
            }
        });
    }

$(document).ready(function() {
    $("#usetab").click(function() { switchTab("use"); });
    $("#presettab").click(function() { switchTab("preset"); });
    $("#typetab").click(function() { switchTab("type"); });
    $("#moduletab").click(function() { switchTab("module"); });
    $("#btn-select-all").click(function() { selectAll(); });
    $("#btn-deselect-all").click(function() { deselectAll(); });
    $("#btn-run-scan").click(function() { submitForm(); });

    $('#scantarget').popover({ 'html': true, 'animation': true, 'trigger': 'focus'});
    $('[data-toggle="popover"]').popover();
});
