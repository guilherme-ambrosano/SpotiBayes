
var _table_ = document.createElement("table"),
    _thead_ = document.createElement("thead"),
    _tbody_ = document.createElement("tbody"),
    _tr_ = document.createElement("tr"),
    _th_ = document.createElement("th"),
    _td_ = document.createElement("td"),
    _br_ = document.createElement("br");

function buildHtmlTable(arr) {
    var table = _table_.cloneNode(false);
    table.setAttribute("class", "table table-bordered table-striped table-sm");
    table.setAttribute("id", "tabela_musicas");
    var tbody = _tbody_.cloneNode(false);

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
        tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    return table;
}
            

function addAllColumnHeaders(arr, table) {
    var columnSet = [];
    var tr = _tr_.cloneNode(false);
    var th = _th_.cloneNode(false);
    var thead = _thead_.cloneNode(false);
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
    thead.appendChild(tr);
    table.appendChild(thead);
    return columnSet;
}

function getAllIndexes(arr, val) {
    var indexes = [], i = -1;
    while ((i = arr.indexOf(val, i+1)) != -1){
        indexes.push(i);
    }
    return indexes;
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

    var div_titulo = document.createElement("div");
    div_titulo.setAttribute("id", "div_titulo");
    div_titulo.setAttribute("class", "row");
    var titulo = document.createElement("h2");
    var soma = 0;
    for(var i = 0; i < fits[variavel][parametro].length; i++ ){
        soma += fits[variavel][parametro][i];
    }
    var media = soma/fits[variavel][parametro].length;
    var parametro_txt = parametro.concat(": ").concat(media.toString());
    titulo.appendChild(document.createTextNode(parametro_txt));
    div_titulo.appendChild(titulo);
    div_parametros_col.appendChild(div_titulo);

    var y = fits[variavel][parametro].map(Number);

    var div_traceplot = document.createElement("div");
    div_traceplot.setAttribute("class", "row justify-content-center");
    div_traceplot.setAttribute("style", "width:800px;height:600px;float:none;margin:0 auto;");
    div_traceplot.setAttribute("id", "traceplot");
    var div_histograma = document.createElement("div");
    div_histograma.setAttribute("class", "row justify-content-center");
    div_histograma.setAttribute("style", "width:800px;height:600px;float:none;margin:0 auto;");
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

    var div_titulo = document.createElement("div");
    div_titulo.setAttribute("id", "div_titulo");
    div_titulo.setAttribute("class", "row");
    var titulo = document.createElement("h2");
    titulo.appendChild(document.createTextNode(variavel));
    div_titulo.appendChild(titulo);
    div_variaveis_col.appendChild(div_titulo);

    var y_var = json_p_array(JSON.parse(dentro), variavel).map(Number);
    var titulos_texto = json_p_array(JSON.parse(dentro), "Título");
    var y_var_selected = json_p_array(JSON.parse(dentro), variavel.concat("_Bool"))
        .map(function(item, i) {
            if (item) {
                return y_var[i];
            }
            return null;
        })
        .filter(function(item) {
            return item != null;
        });

    var selected = [];
    
    for (var i = 0, maxi = y_var_selected.length; i < maxi; i++) {
        indices = getAllIndexes(y_var, y_var_selected[i]);
        for (var j = 0, maxj = indices.length; j < maxj; j++) {
            selected.push(indices[j]);
        }
    }

    console.log(selected);

    var div_boxplot = document.createElement("div");
    div_boxplot.setAttribute("class", "row justify-content-center");
    div_boxplot.setAttribute("style", "width:700px;height:450px;float:none;margin:0 auto;");
    div_boxplot.setAttribute("id", "boxplot");
    var div_histograma_var = document.createElement("div");
    div_histograma_var.setAttribute("class", "row justify-content-center");
    div_histograma_var.setAttribute("style", "width:700px;height:450px;float:none;margin:0 auto;");
    div_histograma_var.setAttribute("id", "histograma_var");

    div_variaveis_col.appendChild(div_boxplot);
    div_variaveis_col.appendChild(div_histograma_var);

    Plotly.newPlot(div_boxplot, [{
        y: y_var,
        text: titulos_texto,
        boxpoints: "all",
        selectedpoints: selected,
        selected: {
          marker: {
            color: '#b3cde3'
          }
        },
        unselected: {
          marker: {
            color: '#fbb4ae'
          }
        },
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
    var div_loading = document.getElementById("div_loading");
    if (!(div_loading==null)) {
        div_loading.parentNode.removeChild(div_loading);
    }

    var dados = dados_completos.fits;

    var div_resultados = document.getElementById("div_resultados_col");

    var div_tabela_musicas = document.createElement("div");
    var div_tabela_musicas_col = document.createElement("div");
    div_tabela_musicas.setAttribute("class", "row");
    div_tabela_musicas_col.appendChild(buildHtmlTable(JSON.parse(dados_completos.dentro)));
    div_tabela_musicas.appendChild(div_tabela_musicas_col);

    var div_form_variaveis = document.createElement("div");
    div_form_variaveis.setAttribute("id", "div_form_variaveis");
    div_form_variaveis.setAttribute("class", "form-group row");

    div_resultados.appendChild(div_tabela_musicas);
    div_resultados.appendChild(div_form_variaveis);
    
    $('#tabela_musicas').DataTable({
        "scrollY": "50vh",
        "scrollCollapse": true,
        });
    $('.dataTables_length').addClass('bs-select');

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


function construir_div_error(dados_completos) {
    var div_loading = document.getElementById("div_loading");
    if (!(div_loading==null)) {
        div_loading.parentNode.removeChild(div_loading);
    }

    var div_resultados = document.getElementById("div_resultados_col");

    var div_erro = document.createElement("div");
    div_erro.setAttribute("class", "row my-4");
    div_erro.appendChild(document.createTextNode("Erro ao carregar a playlist."));

    div_resultados.appendChild(div_erro);
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

    var div_loading = document.createElement("div");
    div_loading.setAttribute("id", "div_loading");
    div_loading.setAttribute("class", "row d-flex min-vh-100 justify-content-center align-items-center");

    var spinner = document.createElement("div");
    spinner.setAttribute("class", "spinner-border");
    spinner.setAttribute("role", "status");

    var loading = document.createElement("span");
    loading.setAttribute("class", "sr-only");
    loading.appendChild(document.createTextNode("Loading..."));

    spinner.appendChild(loading);
    div_loading.appendChild(spinner);

    $.get("/get_posterior", {"playlist": pl})
        .done(construir_div_resultados)
        .fail(construir_div_error);

    div_titulo.appendChild(titulo);
    div_resultados_col.appendChild(div_titulo);
    div_resultados_col.appendChild(div_loading);
    div_resultados.appendChild(div_resultados_col);
    div_main.appendChild(div_resultados);
}

$("#playlists").on("change", mudar_playlist);

$(document).ready(function () {
    });