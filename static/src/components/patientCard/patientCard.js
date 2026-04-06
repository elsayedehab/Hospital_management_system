/** @odoo-module **/

import { Component, useState, onWillUnmount,useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PatientCard extends Component {
    static template = "Hospital_mangement.PatientCard";

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            patient_data: [],
            isInputVisible:false,
        });

        this.nameInput=useRef("nameInput");
        this.birthInput=useRef("birthInput");
        this.genderInput=useRef("genderInput");

        this.loadrecords();
        
        this.interval_id = setInterval(() => {
            this.loadrecords();
        }, 3000);

        onWillUnmount(() => {
            clearInterval(this.interval_id);
        });
    }

    async loadrecords() {
        try {
            const res = await this.rpc("/web/dataset/call_kw/", {
                model: "hospital.patient",
                method: "search_read",
                args: [[]],
                kwargs: {
                    fields: ["name", "age", "gender", "active", "date_of_birth"]
                }
            });
            console.log("Data Received:", res);
            this.state.patient_data = res;
        } catch (error) {
            console.error("RPC Error:", error);
        }
    }

    async createrecord(){
        const name = this.nameInput.el.value;
        const dob = this.birthInput.el.value;
        const gender = this.genderInput.el.value;

        if (!name) {
            alert("Please enter a name!");
            return;
        }
        try {
            const res=await this.rpc("/web/dataset/call_kw/",{
                model:"hospital.patient",
                method:"create",
                args:[[{
                    name: name,
                    date_of_birth: dob,
                    gender: gender,
                
                }]],
                kwargs:{},
            })
            this.nameInput.el.value = "";
            this.loadrecords();
        }catch(error){
            console.log("RPC Error:", error);
        }

    }

    toggleInputForm() {
    this.state.isInputVisible = !this.state.isInputVisible;
}
}

registry.category("actions").add("Hospital_mangement.patientcard_action", PatientCard);