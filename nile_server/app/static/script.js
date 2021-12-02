$(document).ready(function() {

    /**
     Initialize local variables
    */
    var $sortBy = "workers"
    var $tableRows = $('.table-select'); 
    var $selectedTest = ""
    var list = {{ tests|tojson }};
    document.getElementById("view-test").innerHTML = "Select Test"

    /**
    * Highlight a selected a table row
    */ 
    $('.table-select').click(function(e) {
        $tableRows.removeClass('selected');
        $(this).addClass('selected');
        $selectedTest = $(this).find('th:first').text()
        document.getElementById("view-test").innerHTML =  "View Test " + $selectedTest
    });

    /**
    * Sort rows based on selected dropdown item
    */  
    $(".dropdown-menu a").click(function(){
        $sortBy = this.id;
        console.log($sortBy)

        $(".dropdown-toggle:first-child").text($(this).text());
        $(".dropdown-toggle:first-child").val($(this).text());
        
        if ($sortBy === "start") {
            list.sort(function(a, b) {
                a = new Date(a.start);
                b = new Date(b.start);
                return a < b ? -1 : a > b ? 1 : 0;
            });
        } else if ($sortBy === "workers") {
            list.sort((a, b) => b.workers - a.workers);
        } else if ($sortBy === "id") {
            list.sort((a, b) => a.id - b.id);
        }

        list.forEach(iterate)
        function iterate(test, index) 
        { 
            console.log(test)
            index += 1
            document.getElementById(index + '-id').innerHTML = test.id
            document.getElementById(index + '-cfg').innerHTML = test.config
            document.getElementById(index + '-start').innerHTML = test.start
            document.getElementById(index + '-end').innerHTML = test.end
            document.getElementById(index + '-workers').innerHTML = test.workers
        }

    });
    
    $("#view-summary").click(function() {
        console.log("view sum")
        window.open("http://localhost:5000/tests/" + $selectedTest,"_self")
    });
    
})
