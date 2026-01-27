  let datos_pdf_editables = {};
  let global_a = [];
function editarArr(id) {
 const arrendatario = global_a.find(a => a.id === id);
 if (!arrendatario) {
  console.log("Arrendatario no encontrado");
  return; 
}
  // 3. Mostrar en consola (para verificar)
  console.log(" Arrendatario seleccionado:", arrendatario);
  idedited = id;
  document.getElementById("arrendatario_id").value = id;
  

  // Prellenar los display fields (textos)
  document.getElementById("display_nombre").textContent = arrendatario.nombre_arrendatario;
  document.getElementById("display_ubicacion").textContent = arrendatario.nombre_ubicacion;
  document.getElementById("display_direccion").textContent = arrendatario.direccion_ubicacion;
  document.getElementById("display_personas").textContent = arrendatario.personas_por_arrendatario || "-";
  document.getElementById("display_telefono").textContent = arrendatario.telefono || "-";
  document.getElementById("display_email").textContent = arrendatario.email || "-";

  // Prellenar los inputs (ocultos por ahora)
  document.getElementById("input_nombre").value = arrendatario.nombre_arrendatario;
  document.getElementById("input_ubicacion").value = arrendatario.nombre_ubicacion;
  document.getElementById("input_direccion").value = arrendatario.direccion_ubicacion;
  document.getElementById("input_personas").value = arrendatario.personas_por_arrendatario;
  document.getElementById("input_telefono").value = arrendatario.telefono || "";
  document.getElementById("input_email").value = arrendatario.email || "";

  document.getElementById("containerEditarArrendatario").style.display = "block";
  document.getElementById("formTitle").textContent = "Editar Arrendatario";
}

function edit_mod_activated(){
  modoEdicionInline = true;

  document.querySelectorAll(".display-field").forEach(el => {
    el.style.display = "none";
  });

  document.querySelectorAll(".edit-field").forEach(el => {
    el.style.display = "block";0
  });
  // Cambiar botones
  document.getElementById("btnEditarInline").style.display = "none";
  document.getElementById("btnGuardarInline").style.display = "block";
  document.getElementById("btnCancelarInline").style.display = "block";
  console.log("Modo edición inline ");

}

function cancel_edit_mod(){
  modoEdicionInline = false;

  document.querySelectorAll(".display-field").forEach(el => {
    el.style.display = "block";
  });

  document.querySelectorAll(".edit-field").forEach(el => {
    el.style.display = "none";
  });
  // Cambiar botones
  document.getElementById("btnEditarInline").style.display = "block";
  document.getElementById("btnGuardarInline").style.display = "none";
  document.getElementById("btnCancelarInline").style.display = "none";
  console.log("Canceló edición inline ");
}
async function changes_save_inline (){
const id = document.getElementById("arrendatario_id").value;

  const datosActualizados = {
    nombre_arrendatario: document.getElementById("input_nombre").value,
    nombre_ubicacion: document.getElementById("input_ubicacion").value,
    direccion_ubicacion: document.getElementById("input_direccion").value,
    personas_por_arrendatario: parseInt(document.getElementById("input_personas").value),
    telefono: document.getElementById("input_telefono").value,
    email: document.getElementById("input_email").value
  };

  console.log(" Enviando datos actualizados:", datosActualizados);

  try {
    const res = await fetch(`/api/v1/update_data_db/?arrendatario_id=${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datosActualizados)
    });

    if (!res.ok) {
      throw new Error(`Error ${res.status}: No se pudo actualizar`);
    }

    const respuesta = await res.json();
    console.log("Actualizado correctamente:", respuesta);

    alert(" Arrendatario actualizado correctamente!");

    // Actualizar display fields con los nuevos valores
    document.getElementById("display_nombre").textContent = datosActualizados.nombre_arrendatario;
    document.getElementById("display_ubicacion").textContent = datosActualizados.nombre_ubicacion;
    document.getElementById("display_direccion").textContent = datosActualizados.direccion_ubicacion;
    document.getElementById("display_personas").textContent = datosActualizados.personas_por_arrendatario;
    document.getElementById("display_telefono").textContent = datosActualizados.telefono || "-";
    document.getElementById("display_email").textContent = datosActualizados.email || "-";

    // Volver a modo lectura
    cancel_edit_mod();

    // Recargar la lista de cards
    cargarArrendatarios();

  } catch (error) {
    console.error(" Error al guardar:", error);
    alert(" Error: " + error.message);
  }
}

// Event listeners
document.getElementById("pdfEdit_preview").addEventListener("click", generar_preview_pdf);
document.getElementById("btnEditarInline").addEventListener("click", edit_mod_activated);
document.getElementById("btnGuardarInline").addEventListener("click", changes_save_inline);
document.getElementById("btnCancelarInline").addEventListener("click", cancel_edit_mod);

// Cargar y mostrar arrendatarios en cards
async function cargarArrendatarios() {
  try {
    const respuesta = await fetch("/Arrendatarios/");
    if (!respuesta.ok) {
      throw new Error(`Error al obtener los arrendatarios: ${respuesta.status}`);
    }
    const data = await respuesta.json();
    const items = data.data || [];
    global_a = items;     
    // Renderizar como cards similar al preview
    const container = document.getElementById("listar_arrendatarios");
    if (items.length === 0) {
      container.innerHTML = "<p style='text-align:center; color:#999;'>No hay arrendatarios registrados</p>";
      return;
    }
    
    container.innerHTML = items.map(a => `
      <div style="border:1px solid #e0e0e0; border-radius:8px; padding:12px; background:#f9f9f9; transition: all 0.2s ease;">
        <p style="margin:8px 0;"><strong style="color:#667eea;">Nombre:</strong> ${a.nombre_arrendatario}</p>
        <p style="margin:8px 0;"><strong style="color:#667eea;">Ubicación:</strong> ${a.nombre_ubicacion}</p>
        <p style="margin:8px 0;"><strong style="color:#667eea;">Dirección:</strong> ${a.direccion_ubicacion}</p>
        <p style="margin:8px 0;"><strong style="color:#667eea;">Personas:</strong> ${a.personas_por_arrendatario ?? "-"}</p>
        <p style="margin:8px 0;"><strong style="color:#667eea;">Tel:</strong> ${a.telefono ?? "-"}</p>
        <p style="margin:8px 0;"><strong style="color:#667eea;">Email:</strong> ${a.email ?? "-"}</p>
        <button class="bubbles" onclick="editarArr(${a.id})" style="margin-top:10px;">
          <span class="text">Editar</span>
        </button>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error en la solicitud GET:", error);
    document.getElementById("listar_arrendatarios").innerHTML = `<p style="color:red;">Error al cargar los datos</p>`;
  }
}

document.getElementById("buttonModifyDB").addEventListener("click", cargarArrendatarios);


document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const buttonPreview = document.getElementById("buttonPreview");
  const previewEl = document.getElementById("previewoutput");
  const ubicacionEl = document.getElementById("ubicacion");
  const listEl = document.getElementById("previewList");
  const totalAgregadoEl = document.getElementById("totalAgregado");

  const getFormValues = () => ({
    WaterValue: document.getElementById("WaterValue").value || 0,
    LuzValue: document.getElementById("LuzValue").value || 0,
    GasValue: document.getElementById("GasValue").value || 0,
    AseoValue: document.getElementById("AseoValue").value || 0,
    Selecionador: document.getElementById("opciones").value
  });

  buttonPreview.addEventListener("click", async (e) => {
    e.preventDefault();

    const values = getFormValues();
    const formData = new FormData();
    formData.append("WaterValue", values.WaterValue);
    formData.append("LuzValue", values.LuzValue);
    formData.append("GasValue", values.GasValue);
    formData.append("AseoValue", values.AseoValue);
    formData.append("Selecionador", values.Selecionador);

    try {
      const res = await fetch("/PreviewComprobantes/", {
        method: "POST",
        body: formData
      });
      if (!res.ok) {
        throw new Error("Error en preview");
      }
      const data = await res.json();
      

    datos_pdf_editables = {};
    data.arrendatarios.forEach((a) => { 
      datos_pdf_editables[a.id] = {
        id: a.id,
        nombre : a.nombre_arrendatario,
        ubicacion : a.nombre_ubicacion,
        direccion : a.direccion_ubicacion,
        personas : a.personas_por_arrendatario,
        servicios: [
          {descripcion: "Luz", valor: a.servicios.luz},
          {descripcion: "Agua", valor: a.servicios.agua},
          {descripcion: "Gas", valor: a.servicios.gas},
          {descripcion: "Aseo", valor: a.servicios.aseo}
        ]
      };
      })
      console.log("Datos para PDF editables:", datos_pdf_editables);
      // Render del preview
      ubicacionEl.textContent = data.ubicacion;
      totalAgregadoEl.textContent = `$ ${data.sum_total.toFixed(2)}`;

      // Lista por arrendatario
      
      listEl.innerHTML = "";
      data.arrendatarios.forEach((a) => {
        const servicios_html = generate_all_services_html(a.id);
        const card = document.createElement("div");
        card.style.padding = "10px";
        card.style.marginBottom = "10px";
        card.style.border = "1px solid #ddd";
        card.style.borderRadius = "8px";
        card.innerHTML = `
          <div style="border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 10px;">   
            <p><strong>${a.nombre_arrendatario}</strong> (${a.personas_por_arrendatario} persona(s))</p>
            <p>Dirección: ${a.direccion_ubicacion}</p>
          </div>
          
          <!-- CONTENEDOR ESPECÍFICO PARA SERVICIOS -->
          <div data-servicios-container="${a.id}">
            ${servicios_html}
          </div>
          
          <div style="border-top: 2px solid #667eea; padding-top: 10px; margin-top: 10px;">
           <p><strong>Total:</strong> <span id="total-persona-${a.id}">$ ${a.total.toFixed(2)}</span></p>
           </div>

           <div style="display:flex; gap:8px; margin-top:10px;">
            <button 
            class="btn-editar-preview" 
            data-persona-id="${a.id}"
                  style="flex:1; padding:8px; background:#667eea; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:600;"

         >
         Editar
            </button>

            <button 
              class="btn-guardar-preview" 
              data-persona-id="${a.id}" 
              style="flex:1; padding:8px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:600; display:none;"
            >
            Guardar
    </button>
    
    <button 
      class="btn-cancelar-preview" 
      data-persona-id="${a.id}" 
      style="flex:1; padding:8px; background:#dc3545; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:600; display:none;"
    >
     Cancelar
    </button>
    
    <button 
      class="btn-agregar-concepto" 
      data-persona-id="${a.id}" 
      style="flex:1; padding:8px; background:#ffc107; color:#333; border:none; border-radius:5px; cursor:pointer; font-weight:600; display:none;"
    >
      Agregar
    </button>
  </div>
        `;
        listEl.appendChild(card);
      });

      previewEl.classList.add("show");
    } catch (err) {
      console.error(err);
      alert("No se pudo generar la vista previa.");
    }
  });
});
function edit_preview_mod(personaId){
  console.log(`Modo edición preview activado ${personaId}`);
  // Ocultar spans y mostrar inputs
  document.querySelectorAll('span.display-value-preview[data-persona-id="' + personaId + '"]').forEach(el => {
    el.style.display = "none";
  });
  document.querySelectorAll('input.edit-value-preview[data-persona-id="' + personaId + '"]').forEach(el => {
    el.style.display = "inline-block";
  });

  // Cambiar botones
  document.querySelectorAll('.btn-guardar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "block";  });
  document.querySelectorAll('.btn-cancelar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "block";  });
  document.querySelectorAll('.btn-agregar-concepto[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "block";  });
  document.querySelectorAll('.btn-editar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "none";  });

}

function cancel_preview_mod(personaId) {
    console.log(`Modo edición preview cancelado ${personaId}`);
  // Ocultar spans y mostrar inputs
  document.querySelectorAll('span.display-value-preview[data-persona-id="' + personaId + '"]').forEach(el => {
    el.style.display = "block";
  });
  document.querySelectorAll('input.edit-value-preview[data-persona-id="' + personaId + '"]').forEach(el => {
    el.style.display = "none";
  });

  // Cambiar botones
  document.querySelectorAll('.btn-guardar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "none";  });
  document.querySelectorAll('.btn-cancelar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "none";  });
    document.querySelectorAll('.btn-agregar-concepto[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "none";  });
  document.querySelectorAll('.btn-editar-preview[data-persona-id="' + personaId + '"]').forEach(el => { 
    el.style.display = "block";  });

}
function save_preview_mode(personaId){
   
  console.log('Guardando cambios' + personaId);
  
  const inputs = document.querySelectorAll('input.edit-value-preview[data-persona-id="' + personaId + '"]');
  
  inputs.forEach(input => { 
    const concepto = input.getAttribute("data-concepto");
    const nuevoValor = parseFloat(input.value) || 0;


    console.log( " Concepto: " + concepto + " Nuevo valor: " + nuevoValor);
    const new_service = datos_pdf_editables[personaId].servicios.find( s => s.descripcion.toLowerCase() === concepto);
    if (!new_service) {
      console.error("Concepto no encontrado");
      return;
    }
    //Nuevo valor
   new_service.valor = nuevoValor;
   console.log("Datos PDF editables actualizados:", datos_pdf_editables[personaId]);
    const span = document.querySelector(`.display-value-preview[data-persona-id="${personaId}"][data-concepto="${concepto}"]`)
    span.textContent = `$  ${nuevoValor.toFixed(2)}`;

  })
    
  let total = 0;
  datos_pdf_editables[personaId].servicios.forEach ( s => { 
    total += s.valor;
  });

  document.getElementById(`total-persona-${personaId}`).textContent = `$ ${total.toFixed(2)}`;
  cancel_preview_mod(personaId);
};
async function generar_preview_pdf(){
  console.log(" Generando PDF con datos editados:", datos_pdf_editables);
  if (!datos_pdf_editables || Object.keys(datos_pdf_editables).length === 0){
    return alert (" No hay datos para generar el PDF. Por favor, genere la vista previa primero.");
  }
  const personas = Object.values (datos_pdf_editables);
  const sinServicios = personas.filter(p => !p.servicios || p.servicios.length === 0);
  if (sinServicios.length > 0) {
    return alert (" Algunos arrendatarios no tienen servicios asignados. Por favor, verifique los datos.");
  }
  for (let persona of personas) {
  for (let servicio of persona.servicios) {
    if (!servicio.valor || servicio.valor <= 0) {
      alert(`Servicio ${servicio.descripcion} de ${persona.nombre} tiene valor inválido`);
      return;
    }
  }
  }
  const data = { personas: Object.values (datos_pdf_editables) };
  
  const resp = await fetch ("/api/v1/generar_pdf_editado/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (!resp.ok) {
    console.error(" Error al generar PDF:", resp.statusText);
    return alert (" No se pudo generar el PDF. Intente nuevamente.");
  }

  const blob = await resp.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `comprobantes_editados.${Date.now()}.zip`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
function normalizeDesc(s) { 
  return (s || "").trim().toLowerCase(); 
}
function update_total_preview(personaId){
  if(!datos_pdf_editables[personaId]) return;   
  const persona = datos_pdf_editables [personaId]
  const servicios = persona.servicios;
  const total = servicios.reduce ((suma,  s ) => suma +( s.valor || 0), 0); 
  const totalElement = document.getElementById(`total-persona-${personaId}`) 
  if (!totalElement){
     console.error(" No se encontró el elemento total para la persona ID:", personaId);
     return;

  } 

  totalElement.textContent = `$ ${total.toFixed(2)}`;
  console.log(" Total actualizado para persona ID", personaId, ":", total);
};
function render_card_prev(personaId) {
  const persona = datos_pdf_editables[personaId];
  const serviciosHTML = persona.servicios
    .map(s => generate_service_html(personaId, s))
    .join("");
  
  // Encontrar la card y reemplazar su contenido
  const cardAntigua = document.querySelector(`.card-persona[data-persona-id="${personaId}"]`);
  if (cardAntigua) {
    cardAntigua.innerHTML = `
      <div style="...">
        ${serviciosHTML}
      </div>
    `;
  }
}
function generate_service_html(personaId, servicio){
   const concepto   = normalizeDesc(servicio.descripcion);
   const valorFormato = servicio.valor.toFixed(2);

   return `
    <div style="display:flex; justify-content:space-between; align-items:center; margin:8px 0;">
      <span><strong>${servicio.descripcion}:</strong></span>
      <div>
        <span class="display-value-preview" 
              data-persona-id="${personaId}" 
              data-concepto="${concepto}">
          $ ${valorFormato}
        </span>
        <input 
          type="number"
          class="edit-value-preview" 
          data-persona-id="${personaId}"
          data-concepto="${concepto}"
          value="${valorFormato}" 
          style="display:none; width:100px; padding:5px; border:1px solid #667eea; border-radius:5px;">
      </div>
    </div>
  `;
}
document.getElementById("previewList").addEventListener("click", (e) => {
  const target = e.target;
  
  // Si hizo clic en "Editar"
  if (target.classList.contains("btn-editar-preview")) {
    const personaId = target.getAttribute("data-persona-id");
    edit_preview_mod(personaId);
  }
  
  // Si hizo clic en "Guardar"
  if (target.classList.contains("btn-guardar-preview")) {
    const personaId = target.getAttribute("data-persona-id");
    save_preview_mode(personaId);
  }
  
  // Si hizo clic en "Cancelar"
  if (target.classList.contains("btn-cancelar-preview")) {
    const personaId = target.getAttribute("data-persona-id");
    cancel_preview_mod(personaId);
  }
  if (target.classList.contains("btn-agregar-concepto")) {
    const personaId = target.getAttribute("data-persona-id");
    agregar_concepto(personaId);
  }
});
function agregar_concepto(personaId){
  // 1️⃣ VALIDAR - Descripción
  const descripcion = prompt("¿Nombre del concepto? (ej: Internet, Teléfono)");
  if (!descripcion || descripcion.trim() === "") {
    alert("❌ Por favor ingrese un nombre válido");
    return;
  }

  // 2️⃣ VALIDAR - Valor
  const valor = prompt("¿Valor del concepto?");
  if (!valor || isNaN(valor) || parseFloat(valor) <= 0) {
    alert("❌ Por favor ingrese un valor válido (> 0)");
    return;
  }

  // 3️⃣ CREAR OBJETO
  const nuevoConcepto = {
    descripcion: descripcion.trim(),
    valor: parseFloat(valor)
  };

  // 4️⃣ AGREGAR A datos_pdf_editables
  datos_pdf_editables[personaId].servicios.push(nuevoConcepto);
  console.log("✅ Concepto agregado:", nuevoConcepto);

  // 5️⃣ RE-RENDERIZAR CONTENEDOR (CLAVE: [data-servicios-container])
  const serviciosContainer = document.querySelector(`[data-servicios-container="${personaId}"]`);
  
  if (serviciosContainer) {
    serviciosContainer.innerHTML = datos_pdf_editables[personaId].servicios
      .map(s => generate_service_html(personaId, s))
      .join("");
    console.log("✅ Contenedor re-renderizado");
  } else {
    console.error("❌ No se encontró contenedor de servicios");
    return;
  }

  // 6️⃣ ACTUALIZAR TOTAL
  update_total_preview(personaId);

  alert("✅ Concepto agregado correctamente");
}
function generate_all_services_html(personaId) {
  const persona = datos_pdf_editables[personaId];
  
  if (!persona || !persona.servicios) return "";
  
  // Iterar sobre servicios y generar HTML para cada uno
  return persona.servicios
    .map(servicio => generate_service_html(personaId, servicio))
    .join("");  // Concatenar todo
}