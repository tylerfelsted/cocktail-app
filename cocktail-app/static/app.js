const drink = {};

$(document).ready(function() {
    console.log("hello!");
    
    const myModal = new bootstrap.Modal($("#Modal"));
    $(".list-button").click(async function() {
        drink['drink_id'] = this.dataset.id;
        drink['name'] = this.dataset.name;
        drink['image_url'] = this.dataset.image;
        let res = await axios.get(`/api/drinks/${drink['drink_id']}`);
        let lists = res.data.lists;
        $('#modal-form').children('input').each(function() {
            if(lists.includes(Number($(this).attr('id')))){
                $(this).prop('checked', true);
            } else {
                $(this).prop('checked', false)
            }
        });
        myModal.show();
    });

    $("#save-changes").click(function() {
        $('#modal-form').children('input').each(callAxios);
        myModal.hide();
    })
});

async function callAxios() {
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