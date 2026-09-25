$(document).ready(function () {
  var lenguajeSitio = _spPageContextInfo.webServerRelativeUrl.split("/")[1];

  getNavegacion(_spPageContextInfo.webAbsoluteUrl).then(function (nav) {
    // console.log('Contexto', _spPageContextInfo);
    // console.log(_spPageContextInfo.webAbsoluteUrl);
    // console.log('Nav', nav);


    var tools;

    nav.Nodes.map(function (nodo) {
      if (nodo.CustomProperties.length > 0) {
        nodo.CustomProperties.map(function (property) {
          if (
            property["Key"] === "_nav_esHerramientas" &&
            property["Value"] === "true"
          ) {
            tools = nodo;
            return;
          }
        });
      }
    });

    var menu = {
      Id: "TopMenu",
      Nombre: nav.StartingNodeTitle,
      Link: "/",
      Logo:
        location.protocol +
        "//" +
        location.host +
        "/SiteAssets/Master/img/logo.png",
      TextoAlt: _spPageContextInfo.webDescription,
      LinkSubSite: nav.FriendlyUrlPrefix,
      // LogoSubSite: location.protocol + '//' + location.host + '/SiteAssets/spMpIndex/img/logoSubsitio.png',
      LogoSubSite:
        _spPageContextInfo.webAbsoluteUrl +
        "/SiteAssets/Master/img/logoSubSitio.png",
      // LogoSubSite: "",
      TextoAltSubsite: "Logo BCH Subsitio",
      Botones: ConstruirNodos(nav.Nodes),
      Tools: tools !== undefined ? getToolsProps(tools) : tools,
    };
    var botones = "";
    var totalBotones = menu.Botones.length;

    menu.Botones.map(function (value, i) {
      botones +=
        value.OcultoN1 === "Si"
          ? MenuBtn(
            value.Id,
            value.Texto,
            value.TipoNodo === 1 ? value.Link : value.Link2,
            value.Submenu,
            value.TipoNodo,
            lenguajeSitio,
            totalBotones
          )
          : "";
    });
    $("#s4-workspace").ready(MenuSticky(menu, botones));

    MenuFloat(menu, botones, lenguajeSitio);
  });
});

function getNavegacion(webUrl) {
  var _header = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  };
  var url =
    webUrl +
    "/_api/navigation/menustate?mapprovidername='GlobalNavigationSwitchableProvider'&customproperties='_nav_Ayuda,_nav_Tooltip,_nav_esHerramientas,_nav_MostrarSubItems,_nav_Url,_nav_esPieDePagina,_nav_Visible'";

  return fetch(url, _header)
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      return data;
    });
}

var nodeLevels = ["Submenu", "Items"];

function ConstruirNodos(spTree, nodeId, level) {
  var _level = level ? level : 0;
  return spTree.map(function (node, i) {
    var _nodeId = i + 1;
    var _strNodeId = nodeId ? nodeId + "." + _nodeId : _nodeId.toString();

    var _nodeProperties = node.CustomProperties;
    var _filtroVisibles =
      _nodeProperties.length > 0
        ? node.CustomProperties.filter(function (propiedad) {
          return propiedad.Key === "_nav_Visible";
        })[0]
        : "No";
    var _esVisible =
      _filtroVisibles === undefined
        ? "No"
        : _filtroVisibles !== "No"
          ? _filtroVisibles.Value
          : "No";

    var response = {
      Id: _strNodeId,
      Texto: node.Title,
      Link: node.FriendlyUrlSegment,
      Link2: node.SimpleUrl,
      TipoNodo: node.NodeType,
      Oculto: node.isHidden,
      OcultoN1: _esVisible,
    };

    if (node.Nodes.length > 0) {
      function ownKeys(object, enumerableOnly) {
        var keys = Object.keys(object);
        if (Object.getOwnPropertySymbols) {
          var symbols = Object.getOwnPropertySymbols(object);
          if (enumerableOnly)
            symbols = symbols.filter(function (sym) {
              return Object.getOwnPropertyDescriptor(object, sym).enumerable;
            });
          keys.push.apply(keys, symbols);
        }
        return keys;
      }

      function _objectSpread(target) {
        for (var i = 1; i < arguments.length; i++) {
          var source = arguments[i] != null ? arguments[i] : {};
          if (i % 2) {
            ownKeys(Object(source), true).forEach(function (key) {
              _defineProperty(target, key, source[key]);
            });
          } else if (Object.getOwnPropertyDescriptors) {
            Object.defineProperties(
              target,
              Object.getOwnPropertyDescriptors(source)
            );
          } else {
            ownKeys(Object(source)).forEach(function (key) {
              Object.defineProperty(
                target,
                key,
                Object.getOwnPropertyDescriptor(source, key)
              );
            });
          }
        }
        return target;
      }

      function _defineProperty(obj, key, value) {
        if (key in obj) {
          Object.defineProperty(obj, key, {
            value: value,
            enumerable: true,
            configurable: true,
            writable: true,
          });
        } else {
          obj[key] = value;
        }
        return obj;
      }

      response = _objectSpread(
        _objectSpread({}, response),
        {},
        _defineProperty(
          {},
          nodeLevels[_level],
          ConstruirNodos(node.Nodes, _strNodeId, _level + 1)
        )
      );
    }
    return response;
  });
}

function getToolsProps(menu) {
  var tool = menu.Nodes.map(function (nodo) {
    var ayuda;
    nodo.CustomProperties.map(function (property) {
      if (property["Key"] === "_nav_Ayuda") {
        ayuda = property["Value"];
      }
    });
    var sub = nodo.Nodes.length > 0 ? subMenu(nodo.Nodes) : undefined;
    return {
      Elemento: nodo.FriendlyUrlSegment,
      Titulo: nodo.Title,
      Enlace: nodo.NodeType === 1 ? nodo.FriendlyUrlSegment : nodo.SimpleUrl,
      SubMenu: sub,
      Ayuda: ayuda,
    };
  });

  function subMenu(SubMenu) {
    var menu = SubMenu.map(function (item, i) {
      return {
        Index: i + 1,
        Link: item.SimpleUrl,
        Description: item.Title,
        ToolTip:
          item.CustomProperties[0] === undefined
            ? undefined
            : item.CustomProperties[0].Value,
      };
    });
    return menu;
  }
  return tool;
}

// function _RedirectSearch(nombre) {
//   if ($("#searchBtnControl").length > 0) {
//     window.location = " /busqueda/resultados?K=" + $("#" + nombre).val();
//   }
// }

// function handle(e, nombre) {
//   if (e.keyCode === 13) {
//     if ($("#searchBtnControl").length > 0) {
//       window.location = " /busqueda/resultados?K=" + $("#" + nombre).val();
//     }
//   }
//   return false;
// }

function MenuFloat(menu, botones, lenguaje) {
  var inDesignMode = document.forms[MSOWebPartPageFormName]
    .MSOLayout_InDesignMode.value
    ? true
    : false;
  if (inDesignMode === true) {
    return 0;
  }

  var botonMenu = menu.Botones.filter(function (item) {
    return item.Link === "herramientas"
  })[0];

  var btnCorreo = botonMenu.Submenu.filter(function (subitem) {
    return subitem.Link === "correo"
  })[0];

  // console.log(btnCorreo);

  $("#menu").html(
    '<nav style=" ' +
    (_spPageContextInfo.isAnonymousUser
      ? "top: 0px !important;"
      : inDesignMode
        ? "top: 160px !important;"
        : "top: 80px !important;") +
    '" class="navbar fixed-top navbar-expand-lg navbar-dark bg-azul-prusia"> ' +
    '<div class="d-flex flex-column navSections" >' +
    '<div class="d-flex flex-column desplegarTools" >' +
    '<div class="d-none d-lg-flex flex-row justify-content-end align-items-start menu-tools" id="menu-tools"></div>' +
    "</div>" +
    '<div class="d-flex justify-content-between justify-content-xl-between justify-content-lg-start justify-content-md-between  flex-wrap pb-1 menuNavegacion " >' +
    ' <a class="navbar-brand d-flex flex-wrap flex-row align-items-center " href="' +
    (lenguaje === "EN" ? "/EN/" : "/") +
    '">' +
    '<img src="' +
    menu.Logo +
    '" class="logoImg" width="100" height="100" alt="" loading="lazy">' +
    '<div class="d-flex flex-wrap logoText pl-3 ">' +
    menu.Nombre +
    "</div>" +
    "</a>" +
    '<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#main_nav">' +
    '<span class="navbar-toggler-icon"></span>' +
    "</button>" +
    '<div class="collapse navbar-collapse mainMenu justify-content-end justify-content-xl-end justify-content-lg-start" id="main_nav">' +
    '<div class="d-flex flex-row py-2 px-2 my-2 menuSearchBox">' +
    '<input id="searchBtnControl" type="text" onkeypress="handle(event,' +
    "'searchBtnControl'" +
    ')" placeholder="' +
    "Quiero buscar..." +
    '" class="form-control searchBoxControl" />' +
    '<button type="button" class="ml-2 btn text-light searchBtnControl" onClick="_RedirectSearch(' +
    "'searchBtnControl'" +
    ')"><i class="fas fa-search"></i></button>' +
    "</div>" +
    '<ul class="navbar-nav"> ' +
    botones +
    '<li class="nav-item">' +
    '<a href="' + btnCorreo.Link2 + '" class="btn nav-link btnCorreoMovil">' + btnCorreo.Texto + '</a>' +
    '</li>' +
    '<li class="nav-item dropdown SearchMenuItem">' +
    '<a href="/busqueda" class="nav-link dropdown-toggle justify-content-center" data-toggle="dropdown" aria-expanded="false"><i class="fa fa-search"></i></a>' +
    '<ul class="dropdown-menu dropdown-menu-right">' +
    '<li class="has-submenu"><div class="dropdown-item d-flex flex-row">' +
    '<input id="searchControl" type="text" onkeypress="handle(event,' +
    "'searchControl'" + ')" placeholder="' + "Quiero buscar..." + '" class="form-control searchBoxControl" />' +
    '<button type="button" class="ml-2 btn text-light searchFloatBtnControl" onClick="_RedirectSearch(' +
    "'searchControl'" +
    ')"><i class="fas fa-search"></i></button>' +
    '</div></li>' +
    '</ul></li>' +
    "</ul>" +
    "</div>" +
    "</div>" +
    "</nav>"
  );
  var divTools = document.getElementById("menu-tools");
  if (menu.Tools !== undefined) {
    divTools.appendChild(MenuHerramientas(menu.Tools));
  }
}

function MenuSticky(menu, botones) {

  $("#menu").html(
    '<nav class="navbar  navbar-expand-g navbar-dark bg-azul-prusia"> ' +
    '<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#main_nav">' +
    '  <span class="navbar-toggler-icon"></span>' +
    "</button>" +
    '<div class="collapse navbar-collapse" id="main_nav">' +
    '<ul class="navbar-nav text-azul-prusia"> ' +
    botones +
    "  </ul>" +
    "</div>" +
    "</nav>"
  );
}

function MenuBtn(Id, Texto, Link, Submenu, TipoNodo, lenguaje, totalBotones) {
  var categorias = "";

  $.each(Submenu, function (i, value) {
    categorias += !value.Oculto
      ? MenuSubMenu(
        value.Texto,
        value.TipoNodo === 1 ? Link + "/" + value.Link : value.Link2,
        value.Items,
        value.TipoNodo,
        lenguaje,
        Id,
        totalBotones
      )
      : "";
  });

  return (
    '<li class="nav-item ' +
    (categorias !== "" ? "dropdown" : "") +
    '"> <a class="nav-link dropdown-toggle" href="/' + (lenguaje === "EN" ? "EN/" : "") + Link + '" data-toggle="dropdown" aria-expanded="false"> ' +
    Texto +
    "</a>" +
    (categorias !== ""
      ? '<ul class="dropdown-menu dropdown-menu-right ">' + categorias + "</ul>"
      : "") +
    "    </li>"
  );
}

function MenuSubMenu(Texto, Link, Items, TipoNodo, lenguaje, Id, totalBotones) {
  var subItems = "";
  if (Items != null) {
    $.each(Items, function (i, value) {
      subItems += !value.Oculto
        ? MenuSubItems(
          value.Texto,
          value.TipoNodo === 1 ? Link + "/" + value.Link : value.Link2,
          value.TipoNodo,
          lenguaje
        )
        : "";
    });
  }

  return (
    '<li class="' +
    (subItems !== "" ? "has-submenu" : "") +
    '">' +
    ' <a class="dropdown-item ' +
    (subItems !== "" ? "dropdown-toggle" : "") +
    '" href="' +
    (TipoNodo === 1
      ? "/" + (lenguaje === "EN" ? "EN/" : "") + Link.toString()
      : Link) +
    '"> ' +
    Texto +
    " </a>" +
    (subItems !== ""
      ? '<div class="megasubmenu ' +
      (Id > 4 && "megasubmenuIzq") +
      ' dropdown-menu">' +
      '<div class="d-flex d-flex-column flex-wrap">' +
      subItems +
      "</div>" +
      "</div>"
      : "") +
    "</li>"
  );
}

function MenuSubItems(Texto, Link, TipoNodo, lenguaje) {
  return (
    '<a class="dropdown-item" href="' +
    (TipoNodo === 1
      ? "/" + (lenguaje === "EN" ? "EN/" : "") + Link.toString()
      : Link) +
    '">' +
    Texto +
    "</a>"
  );
}

function MenuHerramientas(Tools) {
  // div Herramientas Opciones
  var divHerramientasOpciones = document.createElement("div");
  divHerramientasOpciones.className =
    "d-flex flex-row justify-content-center align-items-start menu-tools";
  divHerramientasOpciones.id = "menu-tools";
  $.each(Tools, function (i, valor) {
    divHerramientasOpciones.appendChild(getTools(valor));
  });
  return divHerramientasOpciones;
}

function getTools(subMenuTool) {
  // div Opciones Contenedor
  var divOpcionesContenedor = document.createElement("div");
  divOpcionesContenedor.className =
    "d-none d-md-flex align-items-center text-center menu-tools-item px-2";
  // anchor opciones
  var aMenuItem = document.createElement("a");
  aMenuItem.innerText = subMenuTool.Titulo;
  aMenuItem.href = subMenuTool.Enlace ? subMenuTool.Enlace : "#";
  aMenuItem.className = "link";
  var tamanioSubmenu = 0;
  if (subMenuTool.SubMenu !== undefined) {
    tamanioSubmenu = subMenuTool.SubMenu.length;
  }

  if (tamanioSubmenu > 0) {
    divOpcionesContenedor.className += " dropdown";
    aMenuItem.id = "dropdownMenuLink";
    aMenuItem.className += " dropdown-toggle";
    aMenuItem.setAttribute("role", "button");
    aMenuItem.setAttribute("data-toggle", "dropdown");
    aMenuItem.setAttribute("aria-haspopup", "true");
    aMenuItem.setAttribute("aria-expanded", "false");
    if (subMenuTool.SubMenu !== undefined) {
      // div DropDown Contenedor
      var divDropDown = document.createElement("div");
      divDropDown.className = "dropdown-menu";
      divDropDown.setAttribute("aria-labelledby", "dropdownMenuLink");
      $.each(subMenuTool.SubMenu, function (i, valor) {
        // anchor Dropdown Item
        var aDropDownItem = document.createElement("a");
        aDropDownItem.className =
          "d-flex justify-content-center dropdown-item menu-tools-item-submenu-item";
        aDropDownItem.title = valor.ToolTip;
        aDropDownItem.innerText = valor.Description;
        aDropDownItem.href = valor.Link ? valor.Link : "/" + valor.Elemento;
        divOpcionesContenedor.appendChild(aMenuItem);
        divDropDown.appendChild(aDropDownItem);
        divOpcionesContenedor.appendChild(divDropDown);
      });
    }
  } else {
    divOpcionesContenedor.appendChild(aMenuItem);
  }
  if (subMenuTool.Ayuda !== undefined) {
    divOpcionesContenedor.appendChild(
      Popovers(
        "bottom",
        "far fa-question-circle",
        "menu-tools-help-button",
        subMenuTool.Ayuda
      )
    );
  }
  return divOpcionesContenedor;
}

function Popovers(Posicion, Icono, Clase, Texto) {
  var btn = document.createElement("a");
  btn.tabIndex = 0;
  btn.classList = Clase;
  btn.setAttribute("role", "button");
  btn.setAttribute("data-toggle", "popover");
  btn.setAttribute("data-trigger", "focus");
  // btn.setAttribute("data-placement", Posicion);
  btn.setAttribute("data-content", Texto);
  var span = document.createElement("span");
  span.className = Icono;
  btn.appendChild(span);
  return btn;
}

//CAMBIO DE SANITIZACIÓN PD BCH
//Autor: Abner Jeancarlos García Alvarado
//N° Empleado: 700353
//Ticket: 202601867  Fecha: 17/09/2026
function _sanitizarBusqueda(valor){
  var v = (valor || '').trim();
  if (/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9 ]/.test(v)) {
     return { valido: false, mensaje: "Solo se permiten letras y números." };
  }
  if (v.length < 2 || v.length > 50) {
    return { valido: false, mensaje: "Ingrese entre 2 y 50 caracteres." };
  }
  var knownExploits = [
    /\b(select|union|insert|update|delete|drop|truncate|exec|execute|xp_cmd|xp_cmdshell|waitfor|sysobjects|syscolumns|sysusers|sp_password)\b/i,
    /\b(script|iframe|object|embed|onerror|onload|onclick|onmouseover|onfocus)\b/i,
    /\b(eval|alert|confirm|prompt|document|window|location|cookie)\b/i,
    /\b(powershell|bash|sh|cmd|wget|curl|nc|netcat|ncat|chmod|sudo|ping|nslookup)\b/i
  ];
  for (var i = 0; i < knownExploits.length; i++){
    if (knownExploits[i].test(v)){
      return { valido: false, mensaje: "Búsqueda no permitida." };
    }
  } 
  return {valido: true, valor: v};
}

function _mostrarErrorBusqueda(nombre, mensaje) {
  var input = document.getElementById(nombre);
  if(!input) return;

  var errorId = nombre + '_bch_error';
  var errorEl = document.getElementById(errorId);

  if (!errorEl){
    errorEl = document.createElement('div');
    errorEl.id = errorId;
     errorEl.style.cssText = [
            'color:#fff',
            'background:rgba(6, 69, 104, 0.25)',
            'padding:4px 10px',
            'font-size:12px',
            'margin-top:5px',
            'border-radius:3px',
            'width:100%',
            'box-sizing:border-box',
            'display:block',
            'clear:both'].join(';');

          var wrapper = input.parentNode;            // div.dropdown-item.d-flex
          wrapper.parentNode.insertBefore(errorEl, wrapper.nextSibling); // debajo del row input+botón
  }

  errorEl.textContent = mensaje;
  errorEl.style.display = 'block';

  clearTimeout(errorEl._timer);
  errorEl._timer = setTimeout(function() {
    errorEl.style.display = 'none'
  }, 3500);
}

// function contieneHtmlOPreligroso(text){
//   const regex = /<[^>]+>|javascript\s*:|vbscript\s*:|data\s*:|on[a-z]+\s*=|script|iframe|object|embed|svg|eval\s*\(|  Function\s*\(|document\.|window\.|cookie|&#|&[a-z]+;/i;
//   return regex.test(text)
// }

function _RedirectSearch(nombre) {
  if ($("#searchBtnControl").length > 0) {
    var resultado = _sanitizarBusqueda($("#" + nombre).val());
    if  (!resultado.valido){
      _mostrarErrorBusqueda(nombre, resultado.mensaje);
      return;
    }
    window.location = "/busqueda/resultados?K=" + encodeURIComponent(resultado.valor);
  }
}

function handle(e, nombre) {
  if (e.keyCode === 13 || e.which === 13 || e.key === 'Enter') {
    e.preventDefault();
    e.stopPropagation();
    if ($("#searchBtnControl").length > 0) {
      var resultado = _sanitizarBusqueda($("#" + nombre).val());
      if (!resultado.valido){
        _mostrarErrorBusqueda(nombre, resultado.mensaje);
        return false;
      }
      window.location = "/busqueda/resultados?K=" + encodeURIComponent(resultado.valor);
    }
  }
  return false;
}

$(document).on('mousedown', '.SearchMenuItem .searchFloatBtnControl', function (e) {
      e.preventDefault();
    });

$(document.body).on('click', '.SearchMenuItem .searchFloatBtnControl', function (e) {
    e.stopPropagation(); // impide que el click llegue a Bootstrap (que escucha en document)
  });

$(document).on('keydown', '#searchControl, #searchBtnControl', function (e){
  if (e.keyCode === 13 || e.key === 'Enter') {
    e.preventDefault();
    e.stopPropagation();
    if ($("#searchBtnControl").length > 0) {
      var nombre = this.id;
      var resultado = _sanitizarBusqueda($(this).val());
      if(!resultado.valido){
            _mostrarErrorBusqueda(nombre, resultado.mensaje);
      }else {
        window.location = "/busqueda/resultados?K=" + encodeURIComponent(resultado.valor);
      }
    }
  }
});

var _dragFromSearch = false;

$(document).on('mousedown', '.SearchMenuItem .dropdown-menu', function(){
  _dragFromSearch =true;
})

$(document).on('mouseup', function () {
    setTimeout(function () { _dragFromSearch = false; }, 0);
  });

$(document.body).on('click', function (e) {
  if (_dragFromSearch) {
    e.stopPropagation();
  }
});