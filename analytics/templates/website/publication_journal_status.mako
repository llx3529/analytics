## coding: utf-8
<div id="journal_status" style="width:60%; height:400px;">
    <span id="loading_journal_status">
        <img src="/static/images/loading.gif" />
        <h5>${_(u'loading')}</h5>
    </span>
</div>
<script language="javascript">
    $("#loading_journal_status").show();
    $(document).ready(function() {
        var url =  "${request.route_url('publication_journal_status')}?code=${selected_code}&collection=${selected_collection_code}&callback=?";

        $.getJSON(url,  function(data) {
            $('#journal_status').highcharts(data['options']);
            $("#loading_journal_status").hide();
        });
    });
</script>
