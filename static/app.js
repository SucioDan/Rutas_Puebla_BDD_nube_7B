// ============================================
// Rutas Puebla - CRUD de paradas + mapa Leaflet
// ============================================

const API = "/paradas";

const form = document.getElementById("form-parada");
const lista = document.getElementById("lista-paradas");
const mensaje = document.getElementById("mensaje");
const btnCancelar = document.getElementById("btn-cancelar");
const btnGuardar = document.getElementById("btn-guardar");
const titulo = document.getElementById("titulo-formulario");

// ---------- Mapa ----------

const mapa = L.map("mapa").setView([19.0414, -98.2063], 13);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(mapa);

const capaParadas = L.layerGroup().addTo(mapa);
let marcadorSeleccionado = null;
let marcadorFormulario = null;

mapa.on("click", (evento) => {
  const { lat, lng } = evento.latlng;
  document.getElementById("latitud").value = lat.toFixed(6);
  document.getElementById("longitud").value = lng.toFixed(6);

  if (marcadorFormulario) {
    mapa.removeLayer(marcadorFormulario);
  }
  marcadorFormulario = L.marker([lat, lng])
    .addTo(mapa)
    .bindPopup("Ubicación seleccionada")
    .openPopup();
});

// ---------- Utilidades ----------

function escapar(texto) {
  return String(texto).replace(/[&<>"']/g, (c) => {
    const mapaEntidades = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return mapaEntidades[c];
  });
}

function mostrarMensaje(texto, tipo) {
  mensaje.textContent = texto;
  mensaje.className = tipo;
}

function limpiarFormulario() {
  form.reset();
  document.getElementById("parada-id").value = "";
  btnCancelar.classList.add("oculto");
  btnGuardar.textContent = "Guardar";
  titulo.textContent = "Registrar parada";

  if (marcadorFormulario) {
    mapa.removeLayer(marcadorFormulario);
    marcadorFormulario = null;
  }
}

function leerFormulario() {
  const rutas = document
    .getElementById("rutas")
    .value.split(",")
    .map((ruta) => ruta.trim())
    .filter((ruta) => ruta !== "");

  return {
    nombre: document.getElementById("nombre").value.trim(),
    colonia: document.getElementById("colonia").value.trim(),
    municipio: "Puebla",
    latitud: parseFloat(document.getElementById("latitud").value),
    longitud: parseFloat(document.getElementById("longitud").value),
    rutas,
    activa: document.getElementById("activa").value === "true",
  };
}

async function leerError(respuesta, respaldo) {
  try {
    const datos = await respuesta.json();
    if (Array.isArray(datos.detail)) {
      return datos.detail.map((d) => d.msg).join(", ");
    }
    return datos.detail || respaldo;
  } catch {
    return respaldo;
  }
}

// ---------- Carga y render ----------

async function cargarParadas() {
  try {
    const respuesta = await fetch(API);
    if (!respuesta.ok) {
      throw new Error("No se pudo obtener la lista de paradas");
    }

    const datos = await respuesta.json();

    lista.innerHTML = "";
    capaParadas.clearLayers();

    if (!datos.paradas || datos.paradas.length === 0) {
      lista.innerHTML = "<p>No hay paradas registradas.</p>";
      return;
    }

    datos.paradas.forEach((parada) => {
      const tarjeta = document.createElement("article");
      tarjeta.className = "parada";

      const rutas = parada.rutas.length > 0 ? parada.rutas.join(", ") : "Sin rutas";
      const estado = parada.activa ? "Activa" : "Inactiva";

      tarjeta.innerHTML = `
        <h3>${escapar(parada.nombre)}</h3>
        <p><strong>ID:</strong> ${escapar(parada.id)}</p>
        <p><strong>Colonia:</strong> ${escapar(parada.colonia)}</p>
        <p><strong>Municipio:</strong> ${escapar(parada.municipio)}</p>
        <p><strong>Coordenadas:</strong> ${parada.latitud}, ${parada.longitud}</p>
        <p><strong>Rutas:</strong> ${escapar(rutas)}</p>
        <p><strong>Estado:</strong> ${estado}</p>
        <div class="acciones">
          <button class="btn-editar" data-id="${escapar(parada.id)}">Editar</button>
          <button class="btn-eliminar" data-id="${escapar(parada.id)}">Eliminar</button>
          <button class="btn-ubicar" data-id="${escapar(parada.id)}">Ver en mapa</button>
        </div>
      `;

      lista.appendChild(tarjeta);

      const marcador = L.marker([parada.latitud, parada.longitud]).addTo(capaParadas);
      marcador.bindPopup(
        `<strong>${escapar(parada.nombre)}</strong><br>` +
          `${escapar(parada.colonia)}<br>` +
          `Rutas: ${escapar(rutas)}`
      );
      marcador.bindTooltip(parada.nombre);
    });
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

// ---------- Acciones ----------

async function cargarParadaParaEditar(id) {
  try {
    const respuesta = await fetch(`${API}/${encodeURIComponent(id)}`);
    if (!respuesta.ok) {
      throw new Error("No se encontró la parada");
    }

    const parada = await respuesta.json();

    document.getElementById("parada-id").value = parada.id;
    document.getElementById("nombre").value = parada.nombre;
    document.getElementById("colonia").value = parada.colonia;
    document.getElementById("latitud").value = parada.latitud;
    document.getElementById("longitud").value = parada.longitud;
    document.getElementById("rutas").value = parada.rutas.join(", ");
    document.getElementById("activa").value = String(parada.activa);

    btnCancelar.classList.remove("oculto");
    btnGuardar.textContent = "Actualizar";
    titulo.textContent = "Editar parada";

    document.querySelector(".panel").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

async function eliminarParada(id) {
  if (!confirm("¿Deseas eliminar esta parada?")) {
    return;
  }

  try {
    const respuesta = await fetch(`${API}/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });

    if (!respuesta.ok) {
      throw new Error(await leerError(respuesta, "No se pudo eliminar la parada"));
    }

    mostrarMensaje("Parada eliminada correctamente.", "exito");

    if (marcadorSeleccionado) {
      mapa.removeLayer(marcadorSeleccionado);
      marcadorSeleccionado = null;
    }

    limpiarFormulario();
    cargarParadas();
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

async function ubicarParadaEnMapa(id) {
  try {
    const respuesta = await fetch(`${API}/${encodeURIComponent(id)}`);
    if (!respuesta.ok) {
      throw new Error("No se encontró la parada");
    }

    const parada = await respuesta.json();
    const rutas = parada.rutas.length > 0 ? parada.rutas.join(", ") : "Sin rutas";

    if (marcadorSeleccionado) {
      mapa.removeLayer(marcadorSeleccionado);
    }

    marcadorSeleccionado = L.marker([parada.latitud, parada.longitud])
      .addTo(mapa)
      .bindPopup(
        `<strong>${escapar(parada.nombre)}</strong><br>` +
          `${escapar(parada.colonia)}<br>` +
          `Rutas: ${escapar(rutas)}`
      )
      .openPopup();

    mapa.setView([parada.latitud, parada.longitud], 16);
    document.querySelector(".panel-mapa").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
}

// ---------- Eventos ----------

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const id = document.getElementById("parada-id").value;
  const datos = leerFormulario();
  const url = id ? `${API}/${encodeURIComponent(id)}` : API;
  const metodo = id ? "PUT" : "POST";

  try {
    const respuesta = await fetch(url, {
      method: metodo,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!respuesta.ok) {
      throw new Error(await leerError(respuesta, "Error al guardar"));
    }

    mostrarMensaje(
      id
        ? "Parada actualizada correctamente."
        : "Parada registrada correctamente.",
      "exito"
    );

    limpiarFormulario();
    cargarParadas();
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
});

lista.addEventListener("click", (evento) => {
  const boton = evento.target;
  const id = boton.dataset.id;

  if (!id) {
    return;
  }

  if (boton.classList.contains("btn-editar")) {
    cargarParadaParaEditar(id);
  }

  if (boton.classList.contains("btn-eliminar")) {
    eliminarParada(id);
  }

  if (boton.classList.contains("btn-ubicar")) {
    ubicarParadaEnMapa(id);
  }
});

btnCancelar.addEventListener("click", limpiarFormulario);
document.getElementById("btn-recargar").addEventListener("click", cargarParadas);

cargarParadas();
