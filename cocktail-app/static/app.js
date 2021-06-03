const drink = {};

$(document).ready(function() {
    console.log("hello!");
    
    const myModal = new bootstrap.Modal($("#exampleModal"));
    $(".list-button").click(async function(e) {
        console.log("open modal");
        drink['id'] = this.dataset.id;
        drink['name'] = this.dataset.name;
        drink['image'] = this.dataset.image;
        let res = await axios.get(`/api/drinks/${drink['id']}`);
        let lists;
        res.data.lists ? lists = res.data.lists : lists = [];
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
        console.log("close modal");
        // console.log($("#test-checkbox").prop('checked'))
        $('#modal-form').children('input').each(callAxios);
        myModal.hide();
    })
});

async function callAxios() {
    if($(this).prop('checked')) {
        const data = {
            "drink": drink,
            "list": $(this).attr('id')
        }
        console.log(data);
        const res = await axios.post('/api/lists/add', data);
        console.log(res);
    }
}