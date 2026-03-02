import axios from "axios";

export const raspiAPIBaseURL = "/raspi";
export const raspiAPI = axios.create({
    baseURL: raspiAPIBaseURL,
});

export const fetchStateAttributes = async () => {
    return raspiAPI
        .put("/raspi")
        .then(({data}) => {
            return data;
        });
};