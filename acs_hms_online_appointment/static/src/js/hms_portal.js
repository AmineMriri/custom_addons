odoo.define('acs_hms_online_appointment.acs_hms_online_appointment', function (require) {
    "use strict";
    
    require('web.dom_ready');
    var slot_date_input = $("input[name='slot_date']");
    var last_date = $("input[name='last_date']");

    var languages = document.getElementsByClassName("js_change_lang active");
    if (languages.length > 0) { 
        var lang = languages[0].getAttribute('data-url_code', '');
        if (lang.startsWith('es')) {        
            $.datepicker.regional['es'] = {
                closeText: 'Cerrar',
                prevText: '< Ant',
                nextText: 'Sig >',
                currentText: 'Hoy',
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
                dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
                dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
                weekHeader: 'Sm',
                dateFormat: 'yy-mm-dd',
                firstDay: 1,
                isRTL: false,
                showMonthAfterYear: false,
                yearSuffix: ''
            };
            $.datepicker.setDefaults($.datepicker.regional['es']);
        }
    }

    $("#ACSDatePicker").datepicker({
        numberOfMonths: 1,
        format: 'yyyy-mm-dd',
        onSelect: function(date) {
            slot_date_input.val(date);
            var selected_date = moment(date).format('YYYY-MM-DD');
            var records = document.getElementsByClassName("acs_appointment_slot");
            var i;
            var slot_to_show = false;
            var acs_no_slots = document.getElementsByClassName("acs_no_slots");
            for (i = 0; i < records.length; i++) {
                var rec_date = records[i].getAttribute('data-date');
                if (selected_date==rec_date) {
                    records[i].style.display = "";
                    slot_to_show = true;
                } else {
                    records[i].style.display = "none";
                }
            }
            if (slot_to_show==true) {
                acs_no_slots[0].style.display = "none";
            } else {
                acs_no_slots[0].style.display = "";
            }
        },
        minDate: new Date(),
        maxDate: new Date(last_date.val()),
        selectWeek: true,
        inline: true,
    });

    $('.ui-datepicker-current-day').click();
    slot_date_input.val(new Date());

    $('.acs_appointment_slot').click(function() {
        var schedule_slot_input = $("input[name='schedule_slot_id']");
        var acs_slot_selected = document.getElementsByClassName("acs_slot_selected")[0];
        var acs_slot_not_selected = document.getElementsByClassName("acs_slot_not_selected")[0];
        var $each_appointment_slot = $(this).parents().find('.acs_appointment_slot');
        $each_appointment_slot.removeClass('acs_active')
        
        if ($(this).hasClass('acs_active') == true) {
            $(this).removeClass('acs_active');            
            schedule_slot_input.val('');
            if (typeof acs_slot_selected !== 'undefined') {
                acs_slot_selected.style.display = "none";
            }
            if (typeof acs_slot_not_selected !== 'undefined') {
                acs_slot_not_selected.style.display = "";
            }
        } else {
            $(this).addClass('acs_active');
            var slotline_id = $(this).data('slotline-id');
            schedule_slot_input.val(slotline_id);
            if (typeof acs_slot_selected !== 'undefined') {
                acs_slot_selected.style.display = "";
            }
            if (typeof acs_slot_not_selected !== 'undefined') {
                acs_slot_not_selected.style.display = "none";
            }
        }
    });
 
    $("#AcsRecordSearch").on('keyup', function() {
        var input, filter, records, rec, i, txtValue;
        input = document.getElementById("AcsRecordSearch");
        filter = input.value.toUpperCase();
        records = document.getElementsByClassName("acs_physician_block");
        for (i = 0; i < records.length; i++) {
            rec = records[i].getElementsByClassName("acs_physician_name")[0];
            txtValue = rec.textContent || rec.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                records[i].style.display = "";
            } else {
                records[i].style.display = "none";
            }
            var physicians = $(this).parents().find('.appoint_person_panel:visible');
            if (physicians.length) {
                physicians[0].click();
            }
        }
        var search_input = document.getElementById("AcsRecordSearch");
        search_input.focus(); 
    });

    $('.acs_appointment').on('change', "input[name='appoitment_by']", function () {
        var appoitment_by = $(this);
        var $physician_datas = $(this).parents().find('#acs_physician_datas');
        var $department_datas = $(this).parents().find('#acs_department_datas');
        if (appoitment_by.val()=='department') {
            $physician_datas.addClass('acs_hide');
            $department_datas.removeClass('acs_hide');
            var departments = $(this).parents().find('.appoint_department_panel');
            if (departments.length) {
                departments[0].click();
            }
        } else {
            $department_datas.addClass('acs_hide');
            $physician_datas.removeClass('acs_hide');
            var physicians = $(this).parents().find('.appoint_person_panel');
            if (physicians.length) {
                physicians[0].click();
            }
        }

    });

    var appoitment_by = $("input[name='appoitment_by']");
    if (appoitment_by.length) {
        $("input[name='appoitment_by']").change();
        $("input[name='appoitment_by']").attr('checked', true);
    }

});