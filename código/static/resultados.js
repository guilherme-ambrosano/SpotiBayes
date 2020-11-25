
var _table_ = document.createElement("table"),
    _tr_ = document.createElement("tr"),
    _th_ = document.createElement("th"),
    _td_ = document.createElement("td"),
    _br_ = document.createElement("br");

function buildHtmlTable(arr) {
    var table = _table_.cloneNode(false);
    table.setAttribute("class", "table table-bordered");

    var columns = addAllColumnHeaders(arr, table);  // Nomes das colunas vão no <th>

    for (var i = 0, maxi = Object.keys(arr).length; i < maxi; ++i) {
        key_i = Object.keys(arr)[i];

        var th = _th_.cloneNode(false);
        th.setAttribute("scope", "row");
        th.appendChild(document.createTextNode(key_i));

        var tr = _tr_.cloneNode(false);
        tr.appendChild(th);
        if ("Total" in arr[key_i]) {
            if (arr[key_i]["Total"] != true && arr[key_i]["Total"] != null) {
                tr.setAttribute("style", "background-color:#fcae91;");  // Colorir o background das músicas removidas
            }
        }

        for (var j = 0, maxj = columns.length; j < maxj; ++j) {
            key_j = columns[j];
            if (key_j.endsWith("_Bool") || key_j == "Total") {
                continue;
            } else {
                var td = _td_.cloneNode(false);
                cellValue = arr[key_i][key_j];
                td.appendChild(document.createTextNode(arr[key_i][key_j] || ''));
                if (arr[key_i][key_j.concat("_Bool")] != true && arr[key_i][key_j.concat("_Bool")] != null) {
                    td.setAttribute("style", "color:#cb181d;");  // Texto vermelho pros valores fora dos IC
                }
                tr.appendChild(td);
            }
        }
        table.appendChild(tr);
    }
    return table;
}
            

function addAllColumnHeaders(arr, table) {
    var columnSet = [];
    var tr = _tr_.cloneNode(false);
    var th = _th_.cloneNode(false);
    th.setAttribute("scope", "col");
    th.appendChild(document.createTextNode(""));
    tr.appendChild(th);
    for (var i = 0, l = Object.keys(arr).length; i < l; i++) {
        key_i = Object.keys(arr)[i];
        for (var key_j in arr[key_i]) {
            if (arr[key_i].hasOwnProperty(key_j) && columnSet.indexOf(key_j) === -1) {
                if (key_j.endsWith("_Bool") || key_j == "Total") {  // Não colocar os bools no <th>
                    columnSet.push(key_j);
                } else {
                    columnSet.push(key_j);
                    var th = _th_.cloneNode(false);
                    th.setAttribute("scope", "col");
                    th.appendChild(document.createTextNode(key_j));
                    tr.appendChild(th);
                }
            }
        }
    }
    table.appendChild(tr);
    return columnSet;
}

function json_p_array(json, coluna) {
    var arr = [];
    for (var i = 0, l = Object.keys(json).length; i < l; i++)  {
        var k = Object.keys(json)[i]
        arr.push(json[k][coluna]);
    }
    return arr;
}

function construir_div_parametros(fits) {
    var div_parametros_row = document.getElementById("div_parametros_row");
    if (!(div_parametros_row == null)) {
        div_parametros_row.parentNode.removeChild(div_parametros_row);
    }

    div_parametros_row = document.createElement("div");
    div_parametros_row.setAttribute("id", "div_parametros_row");
    div_parametros_row.setAttribute("class", "row");
    
    var div_parametros_col = document.createElement("div");
    div_parametros_col.setAttribute("id", "div_parametros_col");
    div_parametros_col.setAttribute("class", "  col");
    
    var variavel = $("#variavel option:selected").text();
    var parametro = $("#parametro option:selected").text();

    console.log(fits);
    console.log(variavel);
    console.log(parametro);
    console.log(fits[variavel]);
    console.log(fits[variavel][parametro]);

    var y = fits[variavel][parametro].map(Number);

    var div_traceplot = document.createElement("div");
    div_traceplot.setAttribute("class", "row");
    div_traceplot.setAttribute("style", "width:800px;height:600px;");
    div_traceplot.setAttribute("id", "traceplot");
    var div_histograma = document.createElement("div");
    div_histograma.setAttribute("class", "row");
    div_histograma.setAttribute("style", "width:800px;height:600px;");
    div_histograma.setAttribute("id", "histograma");

    div_parametros_col.appendChild(div_traceplot);
    div_parametros_col.appendChild(div_histograma);

    div_parametros_row.appendChild(div_parametros_col);

    var div_variaveis_col = document.getElementById("div_variaveis_col");
    div_variaveis_col.appendChild(div_parametros_row);

    Plotly.newPlot(div_traceplot, [{
        y: y,
        mode: "lines"
    }]);

    Plotly.newPlot(div_histograma, [{
        x: y,
        type: "histogram"
    }])
}

function construir_div_variaveis(dentro, fits) {
    var div_variaveis_row = document.getElementById("div_variaveis_row");
    var div_parametros_row = document.getElementById("div_parametros_row");
    if(!(div_variaveis_row == null)) {
        div_variaveis_row.parentNode.removeChild(div_variaveis_row);
    }
    if(!(div_parametros_row == null)) {
        div_parametros_row.parentNode.removeChild(div_parametros_row);
    }

    div_variaveis_row = document.createElement("div");
    div_variaveis_row.setAttribute("id", "div_variaveis_row");
    div_variaveis_row.setAttribute("class", "row");
    
    var div_variaveis_col = document.createElement("div");
    div_variaveis_col.setAttribute("id", "div_variaveis_col");
    div_variaveis_col.setAttribute("class", "  col");

    var div_resultados = document.getElementById("div_resultados_col");
    
    var variavel = $("#variavel option:selected").text();

    var y_var = json_p_array(JSON.parse(dentro), variavel).map(Number);

    var div_boxplot = document.createElement("div");
    div_boxplot.setAttribute("class", "row");
    div_boxplot.setAttribute("style", "width:800px;height:600px;");
    div_boxplot.setAttribute("id", "boxplot");
    var div_histograma_var = document.createElement("div");
    div_histograma_var.setAttribute("class", "row");
    div_histograma_var.setAttribute("style", "width:800px;height:600px;");
    div_histograma_var.setAttribute("id", "histograma_var");

    div_variaveis_col.appendChild(div_boxplot);
    div_variaveis_col.appendChild(div_histograma_var);

    Plotly.newPlot(div_boxplot, [{
        y: y_var,
        boxpoints: "all",
        jitter: 0.3,
        pointpos: -1.8,
        name: "",
        type: "box"
    }]);

    Plotly.newPlot(div_histograma_var, [{
        x: y_var,
        type: "histogram"
    }]);
    
    var div_form = document.createElement("div");
    div_form.setAttribute("id", "div_form_parametro");
    div_form.setAttribute("class", "form-group row");

    div_variaveis_col.appendChild(div_form);
    div_variaveis_row.appendChild(div_variaveis_col);
    div_resultados.appendChild(div_variaveis_row);

    /*
    $("<label>").appendTo("#div_form_parametro")
        .attr("for", "parametro")
        .attr("id", "label")
        .text("Escolha um parâmetro:");
    */
    
    var sel2 = $("<select>")
        .appendTo("#div_form_parametro")
        .append(
            $("<option>")
            .attr("hidden", true)
            .attr("disabled", true)
            .attr("selected", true)
            .text("Parâmetro")
        );
    
    Object.keys(fits[variavel]).forEach(function(keys) {
        sel2.append(
            $("<option>")
            .attr("value", keys)
            .text(keys)
        );
    });

    sel2.attr("id","parametro");
    div_form.scrollIntoView({behavior: "smooth", block: "center"});
    sel2.on("change", function() {
        construir_div_parametros(fits);
    });

}

function construir_div_resultados(dados_completos) {

    var dados = dados_completos.fits;

    var div_resultados = document.getElementById("div_resultados_col");

    var div_tabela_summary = document.createElement("div");
    div_tabela_summary.setAttribute("class", "row");
    div_tabela_summary.appendChild(buildHtmlTable(JSON.parse(dados_completos.summary)));

    var div_tabela_musicas = document.createElement("div");
    div_tabela_musicas.setAttribute("class", "row");
    div_tabela_musicas.appendChild(buildHtmlTable(JSON.parse(dados_completos.dentro)));

    var div_form_variaveis = document.createElement("div");
    div_form_variaveis.setAttribute("id", "div_form_variaveis");
    div_form_variaveis.setAttribute("class", "form-group row");

    div_resultados.appendChild(div_tabela_summary);
    div_resultados.appendChild(div_tabela_musicas);
    div_resultados.appendChild(div_form_variaveis);
    
    /*
    $("<label>")
        .appendTo("#div_form_variaveis")
        .attr("for", "variavel")
        .text("Escolha uma variável:");
    */

    var sel = $("<select>")
        .appendTo("#div_form_variaveis")
        .append(
            $("<option>")
            .attr("hidden", true)
            .attr("disabled", true)
            .attr("selected", true)
            .text("Variável")
        );

    Object.keys(dados).forEach(function(keys) {
        sel.append(
            $("<option>")
            .attr("value", keys)
            .text(keys)
        );
    });

    sel.attr("id","variavel")
    div_form_variaveis.scrollIntoView({behavior: "smooth", block: "center"});
    sel.on("change", function() {
        construir_div_variaveis(dados_completos.dentro, dados);
    });
        
}

function mudar_playlist() {
    div_resultados = document.getElementById("div_resultados_row");
    if (!(div_resultados==null)) {
        div_resultados.parentNode.removeChild(div_resultados);
    }

    var div_resultados = document.createElement("div");
    div_resultados.setAttribute("id", "div_resultados_row");
    div_resultados.setAttribute("class", "row");
    div_main = document.getElementById("div_main");

    var div_resultados_col = document.createElement("div");
    div_resultados_col.setAttribute("id", "div_resultados_col");
    div_resultados_col.setAttribute("class", "  col");

    var pl = $("#playlists").val();
    var div_titulo = document.createElement("div");
    div_titulo.setAttribute("id", "div_titulo");
    div_titulo.setAttribute("class", "row");
    var titulo = document.createElement("h1");
    titulo.appendChild(document.createTextNode(pl));


    $.get("/get_posterior", {"playlist": pl})
        .done(construir_div_resultados);

    div_titulo.appendChild(titulo);
    div_resultados_col.appendChild(div_titulo);
    div_resultados.appendChild(div_resultados_col);
    div_main.appendChild(div_resultados);
}

$("#playlists").on("change", mudar_playlist);