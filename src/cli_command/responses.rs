
use serde::Deserialize;

#[derive(Deserialize, Debug)]
pub struct Cluster {
    attached: bool,
    cluster_id: String,
    name: String,
    status: String,
    url: String,
    version: String
}