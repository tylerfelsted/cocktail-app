const drink = {};

$(document).ready(function() {
    console.log("hello!");
    
    const myModal = new bootstrap.Modal($("#Modal"));
    $(".list-button").click(async function() {
        //Opens the modal to add drinks to a list
        drink['drink_id'] = this.dataset.id;
        drink['name'] = this.dataset.name;
        drink['image_url'] = this.dataset.image;
        let res = await axios.get(`/api/drinks/${drink['drink_id']}`);
        let lists = res.data.lists;
        $('#modal-form').children('input').each(function() {
            //Checks and unchecks the appropriate checkboxes for the selected drink
            if(lists.includes(Number($(this).attr('id')))){
                $(this).prop('checked', true);
            } else {
                $(this).prop('checked', false)
            }
        });
        myModal.show();
    });

    $("#save-changes").click(function() {
        //Execute this function when the save-changes button is clicked
        $('#modal-form').children('input').each(callAxios);
        myModal.hide();
    })
});

async function callAxios() {
    //This function is called on each of the checkboxes in the Modal
    const data = {
        "drink": drink,
        "list": $(this).attr('id')
    }
    if($(this).prop('checked')) {
        await axios.post('/api/lists/add-drink', data);
    } else {
        await axios.post('/api/lists/remove-drink', data);
    }
    
}