var variavel = null;
var parametro = null;
var div_resultados = null;
var div_variaveis = null;
var div_parametros = null;

var _table_ = document.createElement('table'),
    _tr_ = document.createElement('tr'),
    _th_ = document.createElement('th'),
    _td_ = document.createElement('td'),
    _br_ = document.createElement("br");

function buildHtmlTable(arr) {
    var table = _table_.cloneNode(false);
    var columns = addAllColumnHeaders(arr, table);  // Nomes das colunas vão no <th>
    for (var i = 0, maxi = Object.keys(arr).length; i < maxi; ++i) {
        var tr = _tr_.cloneNode(false);
        if (arr[i]["Total"] != true && arr[i]["Total"] != null) {
            tr.style = "background-color:#fcae91;";  // Colorir o background das músicas removidas
        }
        for (var j = 0, maxj = columns.length; j < maxj; ++j) {
            if (columns[j].endsWith("_bool") || columns[j] == "Total") {
                continue;
            } else {
                var td = _td_.cloneNode(false);
                cellValue = arr[i][columns[j]];
                td.appendChild(document.createTextNode(arr[i][columns[j]] || ''));
                if (arr[i][columns[j].concat("_bool")] != true && arr[i][columns[j].concat("_bool")] != null) {
                    td.style = "color:#cb181d;";  // Texto vermelho pros valores fora dos IC
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
    for (var i = 0, l = Object.keys(arr).length; i < l; i++) {
        for (var key in arr[i]) {
            if (arr[i].hasOwnProperty(key) && columnSet.indexOf(key) === -1) {
                if (key.endsWith("_bool") || key == "Total") {  // Não colocar os bools no <th>
                    columnSet.push(key);
                } else {
                    columnSet.push(key);
                    var th = _th_.cloneNode(false);
                    th.appendChild(document.createTextNode(key));
                    tr.appendChild(th);
                }
            }
        }
    }
    table.appendChild(tr);
    return columnSet;
}

function json_p_array(json, coluna) {
    arr = [];
    for (var i = 0, l = Object.keys(json).length; i < l; i++)  {
        arr.push(json[i][coluna]);
    }
    return arr;
}

function construir_div_parametros() {
    div_parametros = document.getElementById("div_parametros");
    if (!(div_parametros == null)) {
        div_parametros.parentNode.removeChild(div_parametros);
    }

    div_parametros = document.createElement("div");
    div_parametros.id = "div_parametros";
    div_variaveis = document.getElementById("div_variaveis");
    div_variaveis.append(div_parametros);

    parametro = $("#parametro option:selected").text();

    var y = dados[variavel][parametro].map(Number);

    div_parametros.append(_br_.cloneNode(false));

    var div_traceplot = document.createElement("div");
    var div_histograma = document.createElement("div");

    div_traceplot.style = "width:800px;height:600px;";
    div_histograma.style = "width:800px;height:600px;";

    div_traceplot.id = "traceplot";
    div_histograma.id = "histograma";

    div_parametros.append(div_traceplot);
    div_parametros.append(div_histograma);

    div_traceplot = document.getElementById("traceplot");
    div_histograma = document.getElementById("histograma");

    Plotly.newPlot(div_traceplot, [{
        y: y,
        mode: "lines"
    }]);

    Plotly.newPlot(div_histograma, [{
        x: y,
        type: "histogram"
    }])
}

function construir_div_variaveis() {
    div_variaveis = document.getElementById("div_variaveis");
    if(!(div_variaveis == null)) {
        div_variaveis.parentNode.removeChild(div_variaveis);
    }

    div_variaveis = document.createElement("div");
    div_variaveis.id = "div_variaveis";
    div_resultados = document.getElementById("div_resultados");
    div_resultados.append(div_variaveis);

    div_variaveis.append(_br_.cloneNode(false));

    variavel = $("#variavel option:selected").text();

    var y_var = json_p_array(JSON.parse(dados_completos.dentro), variavel).map(Number);

    div_variaveis.append(_br_.cloneNode(false));

    var div_boxplot = document.createElement("div");
    var div_histograma_var = document.createElement("div");

    div_boxplot.style = "width:800px;height:600px;";
    div_histograma_var.style = "width:800px;height:600px;";

    div_boxplot.id = "boxplot";
    div_histograma_var.id = "histograma_var";

    div_variaveis.append(div_boxplot);
    div_variaveis.append(div_histograma_var);

    div_boxplot = document.getElementById("boxplot");
    div_histograma_var = document.getElementById("histograma_var");

    Plotly.newPlot(div_boxplot, [{
        y: y_var,
        boxpoints: 'all',
        jitter: 0.3,
        pointpos: -1.8,
        type: "box"
    }]);

    Plotly.newPlot(div_histograma_var, [{
        x: y_var,
        type: "histogram"
    }]);
    
    div_variaveis.append(_br_.cloneNode(false));

    var lab2 = $("<label>").appendTo("#div_variaveis")
    .attr("for", "parametro")
    .attr("id", "label").text("Escolha um parâmetro:");
    var sel2 = $("<select>").appendTo("#div_variaveis");
    sel2.append($("<option>").attr("hidden", true).attr("disabled", true)
        .attr("selected", true).text("Parâmetro"));
    Object.keys(dados[variavel]).forEach(function(keys) {
        sel2.append($("<option>").attr("value", keys).text(keys));
    });
    sel2.attr("id","parametro");
    sel2.on("change", construir_div_parametros);
}

function construir_div_resultados(dados_completos) {

    dados = dados_completos.fits

    div_resultados.appendChild(buildHtmlTable(JSON.parse(dados_completos.summary)));
    div_resultados.append(_br_.cloneNode(false));
    div_resultados.appendChild(buildHtmlTable(JSON.parse(dados_completos.dentro)));
    div_resultados.append(_br_.cloneNode(false));

    var lab = $("<label>").appendTo("#div_resultados")
    .attr("for", "variavel").text("Escolha uma variável:");
    var sel = $("<select>").appendTo("#div_resultados");
    sel.append($("<option>").attr("hidden", true).attr("disabled", true)
        .attr("selected", true).text("Variável"));
    Object.keys(dados).forEach(function(keys) {
        sel.append($("<option>").attr("value", keys).text(keys));
    });
    sel.attr("id","variavel");
    sel.on("change", construir_div_variaveis);
}

function mudar_playlist() {
    div_resultados = document.getElementById("div_resultados");
    if (!(div_resultados==null)) {
        div_resultados.parentNode.removeChild(div_resultados);
    }

    div_resultados = document.createElement("div");
    div_resultados.id = "div_resultados";
    document.body.append(div_resultados);

    pl = $("#playlists").val();

    $.get("/get_posterior", {"playlist": pl})
        .done(construir_div_resultados);
}

$("#playlists").on("change", mudar_playlist);