import express from "express";
import bodyparser from "body-parser";
import axios from "axios";

const app = express();
const port = 3000;
const data = {
    name: "Your name",
    entertainment: 200,
    utilities: 50,
    healthcare: 100,
    transport: 300,
    food: 100,
    rent: 500,
    misc: 100,
    total: 1350
};
app.use(express.static("public"));
app.use(bodyparser.urlencoded({extended: true}));

function submitForm() {
    console.log("Submitting form...");
    document.getElementById("profile-form").submit();
}

app.get("/", (req,res) => {
    res.render("index.ejs", {data: data});
});

app.post("/petroom", (req, res) => {
    res.render("petroom.ejs", {data: data});
});
app.listen(port, () => {
    console.log(`Woohoo, port ${port} up and running!`)
});