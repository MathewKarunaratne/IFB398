// Dragging functionality
const drag = (event) => {
    event.dataTransfer.setData("text/plain", event.target.id);
    $('.dropzone').addClass('droppable-hint');
}

const allowDrop = (ev) => {
    ev.preventDefault();
    if (hasClass(ev.target, "dropzone")) {
        addClass(ev.target, "droppable");
    }
}

const clearDrop = (ev) => {
    removeClass(ev.target, "droppable");
}

const drop = (event) => {
    event.preventDefault();
    const data = event.dataTransfer.getData("text/plain");
    const element = document.querySelector(`#${data}`);
    try {
        // remove the spacer content from dropzone
        event.target.removeChild(event.target.firstChild);
        // add the draggable content
        event.target.appendChild(element);
        // remove the dropzone parent
        unwrap(event.target);
    } catch (error) {
        console.warn("can't move the item to the same place");
    }
}

const dragEnd = () => {
    updateDropzones();
}

const updateDropzones = () => {
    // Reset all the dropzones
    var dz = $('<div class="dropzone rounded" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="clearDrop(event)"> &nbsp; </div>');
    $('.dropzone').remove();
    dz.insertAfter('.dropzone-location');
}

// helpers
function hasClass(target, className) {
    return new RegExp('(\\s|^)' + className + '(\\s|$)').test(target.className);
}

function addClass(ele, cls) {
    if (!hasClass(ele, cls)) ele.className += " " + cls;
}

function removeClass(ele, cls) {
    if (hasClass(ele, cls)) {
        var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');
        ele.className = ele.className.replace(reg, ' ');
    }
}

function unwrap(node) {
    node.replaceWith(...node.childNodes);
}

// Remove a card
function removeCard(event) {
    btn = window.event.srcElement
    btn.parentElement.parentElement.remove();
    updateDropzones();
}


// Buttons
document.addEventListener('DOMContentLoaded', function() {
    // Initialise kanban board
    const startingDataElem = $("#starting-data")[0];
    const startingData = startingDataElem.dataset.cardsData;
    if (startingData.length > 2) {
        const cardList = startingData.slice(2, -2).split("), (");
        for (let i = 0; i < cardList.length; i++) {
            addCard(cardList[i]);
        }
    }
    startingDataElem.remove();
    updateDropzones();


    // Adding cards
    function addCard(cardData) {
        let cardDataList = cardData.split(", "); // Convert to list
        // Remove quotes from strings
        cardDataList[3] = cardDataList[3].slice(1, -1);
        cardDataList[4] = cardDataList[4].slice(1, -1);
        cardDataList[5] = cardDataList[5].slice(1, -1);

        // Generate template
        let template = document.getElementById("task-card-template"); // Should probably move this to a higher scope
        let card = template.content.cloneNode(true);

        // Fill in template
        card.querySelector(".card").id = `card_${cardDataList[2]}`;
        card.querySelector(".card").dataset.taskId = cardDataList[2];
        card.querySelector(".task-name").innerHTML = cardDataList[3];
        card.querySelector(".task-desc").innerHTML = cardDataList[4];
        // card.querySelector(".remove-card-btn").onclick = `removeCard(${cardDataList[2]})`;

        // Place template
        let bucket = document.getElementsByClassName("bucket-container")[cardDataList[0]];
        bucket.appendChild(card);
    }


    // Open the add task modal
    let addTaskModalBtn = document.getElementById("add-task-modal-btn");
    addTaskModalBtn.addEventListener("click", openAddTaskModal);

    function openAddTaskModal(e) {
        e.preventDefault();
        $("#add-task-modal").modal("show");
    }


    // Actually adding the task
    let addTaskBtn = document.querySelector("#add-task-btn");
    if (addTaskBtn) { // Check if the button exists, won't exist if there's no unused tasks
        addTaskBtn.addEventListener("click", addTask);
    }

    function addTask(e) {
        e.preventDefault();
        $("#addTask").modal("hide"); // Do this first to hide changes

        const select = document.getElementById("add-task-select");
        let cardData = select.value;
        let cardDataList = cardData.split(", ");
        $(`#add-task-option-${cardDataList[2]}`).remove();

        addCard(cardData);
        updateDropzones();
    }


    // Saving the kanban board
    let saveBoardBtn = document.querySelector("#save-board-btn");
    saveBoardBtn.addEventListener('click', saveBoard);

    function saveBoard(e) {
        e.preventDefault();

        let cards = [];
        let allBuckets = document.getElementsByClassName("bucket-container");

        for (let status = 0; status < allBuckets.length; status++) {
            let bucket = allBuckets[status].children
            let order = 0;
            for (let i = 0; i < bucket.length; i++) {
                if (hasClass(bucket[i], "card")) {
                    cards.push({
                        "taskID": parseInt(bucket[i].dataset.taskId),
                        "status": parseInt(status),
                        "order" : parseInt(order)
                    })
                    order++;
                }
            }
        }

        // $()                    doesn't work here
        // document.querySelector doesn't work here
        // .item(0)               doesn't work here
        // .children[0]           doesn't work here
        // .childNodes[0]         doesn't work here
        // .firstChild            doesn't work here
        // .value                 doesn't work here
        // And I have no idea why.
        let csrf = document.getElementById("csrf-hiding-spot").getElementsByTagName("input")[0].getAttribute("value");

        $.ajax({
            url: '/tasks/updateKanban',
            type: 'POST',
            data: {
                cards: JSON.stringify(cards),
                csrfmiddlewaretoken: csrf
            },
            success: function(response) {
                if (response.success) {
                    console.log("Kanban saved successfully")
                    // Some sort of message to the user would also be good
                } else {
                    console.error("Save response failed:", response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error("Save request failed:", error);
            }
        });
    }
})
