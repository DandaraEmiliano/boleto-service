const byId = (id) => document.getElementById(id);
const issue = byId("issue");
const lookup = byId("lookup");
const fields = byId("fields");
const example = byId("example");
const payer = byId("payer");
const name = byId("name");
const cpf = byId("cpf");
const amount = byId("amount");
const date = byId("date");
const query = byId("query");
const pdf = byId("pdf");
const retry = byId("retry");
const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const statusLabels = { erro: "Com erro", reprocessando: "Reprocessando", enviado: "Enviado" };
let config;
let current;
let operation = 0;

async function api(path, body, method = "GET") {
  const response = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const result = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = result?.detail;
    throw new Error(typeof detail === "string" ? detail : "Confira os campos e tente novamente.");
  }
  if (result === null) throw new Error("A API retornou uma resposta inesperada.");
  return result;
}

function notice(id, message = "", error = false) {
  const element = byId(id);
  element.textContent = message;
  element.dataset.error = error;
}

function fail(id, error) {
  notice(id, error instanceof TypeError ? "Não foi possível conectar à API. Tente novamente." : error.message, true);
}

function updatePayer() {
  cpf.value = config.pagadores[payer.value] || "";
}

function show(boleto) {
  current = boleto;
  byId("result-name").textContent = boleto.nome;
  byId("result-date").textContent = boleto.vencimento.split("-").reverse().join("/");
  byId("result-amount").textContent = currency.format(boleto.valor);
  byId("result-line").textContent = boleto.linha_digitavel;
  byId("result-code").textContent = boleto.codigo;
  const status = byId("status");
  status.textContent = statusLabels[boleto.status] || boleto.status;
  status.dataset.status = boleto.status;
  pdf.href = pathFor(boleto.codigo) + "/pdf";
  retry.hidden = boleto.status !== "erro";
  byId("result-actions").hidden = false;
}

function pathFor(code) {
  return "/boletos/" + encodeURIComponent(code);
}

async function track(code, requestId) {
  for (let attempt = 0; attempt < 10; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    if (requestId !== operation) return;
    const boleto = await api(pathFor(code));
    if (requestId !== operation) return;
    show(boleto);
    if (boleto.status !== "reprocessando") {
      notice("result-feedback", "Reprocessamento concluído.");
      return;
    }
  }
  notice("result-feedback", "Ainda em processamento. Consulte novamente pelo código.");
}

example.addEventListener("click", () => {
  if (config.demo) {
    payer.selectedIndex = 1;
    updatePayer();
    payer.focus();
  } else {
    name.value = "Marina Exemplo";
    cpf.value = "00000000000";
    name.focus();
  }
  amount.value = "149.90";
  const due = new Date();
  due.setDate(due.getDate() + 7);
  date.value = [due.getFullYear(), due.getMonth() + 1, due.getDate()]
    .map((part) => String(part).padStart(2, "0")).join("-");
});

payer.addEventListener("change", updatePayer);
issue.addEventListener("submit", async (event) => {
  event.preventDefault();
  const requestId = ++operation;
  fields.disabled = true;
  example.disabled = true;
  notice("issue-feedback", "Emitindo boleto…");
  try {
    const boleto = await api("/boletos", {
      nome: config.demo ? payer.value : name.value.trim(),
      cpf: cpf.value,
      valor: amount.value,
      vencimento: date.value,
    }, "POST");
    notice("issue-feedback", "Boleto emitido. A primeira tentativa simula uma falha.");
    if (requestId === operation) {
      query.value = boleto.codigo;
      notice("result-feedback");
      show(boleto);
      if (window.matchMedia("(max-width: 740px)").matches) {
        byId("result-title").scrollIntoView({ block: "start" });
      }
    }
  } catch (error) {
    fail("issue-feedback", error);
  } finally {
    fields.disabled = false;
    example.disabled = false;
  }
});

lookup.addEventListener("submit", async (event) => {
  event.preventDefault();
  const code = query.value.trim();
  if (!code) return;
  const requestId = ++operation;
  const button = lookup.querySelector("button");
  button.disabled = true;
  notice("lookup-feedback", "Consultando…");
  try {
    const boleto = await api(pathFor(code));
    notice("lookup-feedback", "Boleto encontrado.");
    if (requestId !== operation) return;
    notice("result-feedback");
    show(boleto);
    byId("result-title").scrollIntoView({ block: "nearest" });
    if (boleto.status === "reprocessando") await track(code, requestId);
  } catch (error) {
    if (requestId === operation) fail("lookup-feedback", error);
  } finally {
    button.disabled = false;
  }
});

retry.addEventListener("click", async () => {
  const code = current.codigo;
  const requestId = ++operation;
  retry.disabled = true;
  notice("result-feedback", "Solicitando reprocessamento…");
  try {
    await api(pathFor(code) + "/reprocessar", undefined, "POST");
    if (requestId !== operation) return;
    show({ ...current, status: "reprocessando" });
    notice("result-feedback", "Acompanhando a atualização do status…");
    await track(code, requestId);
  } catch (error) {
    if (requestId === operation) fail("result-feedback", error);
  } finally {
    retry.disabled = false;
  }
});

try {
  config = await api("/config");
  if (config.demo) {
    byId("select-label").hidden = false;
    byId("name-label").hidden = true;
    name.required = false;
    payer.required = true;
    cpf.readOnly = true;
    for (const person of Object.keys(config.pagadores)) {
      payer.add(new Option(person, person));
    }
  }
  fields.disabled = false;
  example.disabled = false;
} catch (error) {
  fail("issue-feedback", error);
}
