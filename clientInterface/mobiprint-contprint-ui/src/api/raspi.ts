import axios from "axios";

export const raspiAPIBaseURL = "/raspi";
export const raspiAPI = axios.create({
    baseURL: raspiAPIBaseURL,
});

export const sliceData = async (data: string) => {
    return raspiAPI
        .post("/slice", { data })
        .then(({data}) => {
            return data;
        });
};