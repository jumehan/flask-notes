// noinspection JSIgnoredPromiseFromCall

const BASE_URL = "http://localhost:5000/api";

const $cupcakeList = $("#cupcakes-list");
const $cupcakeForm = $("#new-cupcake-form");

/** given data about a cupcake, generate html */

function generateCupcakeHTML(cupcake) {
  return `
    <div data-cupcake-id="${cupcake.id}">
      <li>
        ${cupcake.flavor} / ${cupcake.size} / ${cupcake.rating}
        <button class="delete-button">X</button>
      </li>
      <img class="Cupcake-img"
            src="${cupcake.image}"
            alt="(no image provided)">
    </div>
  `;
}

/** Get initial cupcakes. Returns [{cupcake}, ...]. */

async function getInitialCupcakes() {
  const response = await axios.get(`${BASE_URL}/cupcakes`);
  return response.data.cupcakes;
}

/** put initial cupcakes on page. */

function showInitialCupcakes(cupcakes) {
  for (let cupcakeData of cupcakes) {
    let $cupcake = $(generateCupcakeHTML(cupcakeData));
    $cupcakeList.append($cupcake);
  }
}


/** handle form for adding of new cupcakes */

async function addNewCupcake(evt) {
  evt.preventDefault();

  let flavor = $("#form-flavor").val();
  let rating = $("#form-rating").val();
  let size = $("#form-size").val();
  let image = $("#form-image").val();

  const newCupcakeResponse = await axios.post(`${BASE_URL}/cupcakes`, {
    flavor,
    rating,
    size,
    image,
  });

  let newCupcake = $(generateCupcakeHTML(newCupcakeResponse.data.cupcake));
  $cupcakeList.append(newCupcake);
  $cupcakeForm.trigger("reset");
}

$cupcakeForm.on("submit", addNewCupcake);


/** handle clicking delete: delete cupcake */

async function deleteCupcake(evt) {
  evt.preventDefault();

  let $cupcake = $(evt.target).closest("div");
  let cupcakeId = $cupcake.attr("data-cupcake-id");

  await axios.delete(`${BASE_URL}/cupcakes/${cupcakeId}`);
  $cupcake.remove();
}

$cupcakeList.on("click", ".delete-button", deleteCupcake);


async function start() {
  const cupcakes = await getInitialCupcakes();
  showInitialCupcakes(cupcakes);
}


start()