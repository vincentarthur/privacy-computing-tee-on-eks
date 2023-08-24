import React, {useState, useEffect} from 'react';
import {
    Button,
    SpaceBetween,
    FormField, Grid, Form, Container, Header, Textarea, Table
} from '@cloudscape-design/components';
import {CustomAppLayout} from './common/common-components';
import {CustomNavi} from './CustomNavi';

import axios from 'axios'
import Magnifier from "react-magnifier";

const HEADERS = {
    "Content-Type": "application/json",
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*'
}

function App({distributions}) {

    const [candidate_images, setCandidateImages] = useState([])
    const [preview, setPreview] = useState("#")
    const [prediction_result, setPredictionResult] = useState('')
    const [image_location, setImageLocation] = useState('')
    const [
        selectedItems,
        setSelectedItems
    ] = React.useState([]);

    useEffect(() => {
        // axios({ method: 'GET', url: 'http://client-svc.fl.svc.cluster.local:5050/list_images', headers: HEADERS}).then(response => {
        fetch_candiadte_images()
    }, []);


    /**
     * Raise request to backend system to get all IMAGES
     */
    function fetch_candiadte_images() {

        axios({
            method: 'GET',
            url: '/api/list_images',
            headers: HEADERS
        })
            .then(response => {
                console.log(response.data);
                setCandidateImages(response.data.images)
                let _entry_list = [];
                if (response['data']) {
                    // Filter modules by different types
                    response['data']['images'].forEach((item) => {

                        let _item = {}
                        _item['image_name'] = item.image_name
                        _item['image_location'] = item.image_location
                        _item['last_modified'] = item.last_modified
                        _item['presigned_url'] = item.presigned_url

                        // Add to list
                        _entry_list.push(_item)
                    });
                }

                setCandidateImages(_entry_list)
            })
    }


    /**
     * Raise request for PREDICTION
     */
    function predict(_image_s3_path) {

        axios.post('/api/predict',
            {
                'image_s3_path': _image_s3_path
            })
            .then((response) => {
                console.log(response.data);
                setPredictionResult(response.data)
            });

    }


    const CandidateImagesTable = () => {

        return (
            <Form>
                <Table
                    onSelectionChange={({detail}) => {
                        setSelectedItems(detail.selectedItems)
                        setPreview(detail.selectedItems[0].presigned_url)
                        setImageLocation(detail.selectedItems[0].image_location)
                    }}
                    selectedItems={selectedItems}
                    ariaLabels={{
                        selectionGroupLabel: "Image Selection",
                        allItemsSelectionLabel: ({selectedItems}) =>
                            `${selectedItems.length} ${
                                selectedItems.length === 1 ? "item" : "items"
                            } selected`,
                        itemSelectionLabel: ({selectedItems}, item) =>
                            item.name
                    }}
                    columnDefinitions={[
                        {
                            id: "image_name",
                            header: "Image Name",
                            cell: e => e.image_name,
                            sortingField: "image_name",
                            isRowHeader: true
                        },
                        {id: "image_location", header: "image_location", cell: e => e.image_location},
                        {id: "presigned_url", header: "presigned_url", cell: e => e.presigned_url},
                        {id: "last_modified", header: "Last Modified Date", cell: e => e.last_modified},
                    ]}
                    columnDisplay={[
                        {id: "image_name", visible: true},
                        {id: "image_location", visible: true},
                        {id: "presigned_url", visible: false},
                        {id: "last_modified", visible: true},
                    ]}
                    items={candidate_images}
                    loadingText="Loading resources"
                    selectionType="single"
                    trackBy="image_name"
                    wrapLines
                    // resizableColumns
                    header={
                        <Header> Select Medical Image for Prediction </Header>
                    }
                />
            </Form>
        )
    }

    const PreviewPanel = () => {

        return (
            <form onSubmit={e => e.preventDefault()}>
                <Form
                    variant="embedded"
                    actions={
                        <SpaceBetween direction="horizontal" size="xs">
                            <Button variant="primary" onClick={(e) => predict(image_location)}>Predict</Button>
                        </SpaceBetween>
                    }
                    header={<Header variant="h3">Image Preview</Header>}
                >
                    <Container>
                        <Magnifier src={preview}/>
                    </Container>
                </Form>
            </form>
        )
    }

    const ResultPanel = () => {
        return (
            <Container
                header={
                    <Header variant="h3">Prediction Result</Header>
                }
            >
                <Textarea
                    value={prediction_result}
                    placeholder="Prediction Result will be displayed here (Wait around 10-20 seconds)."
                    readOnly
                    rows={8}
                />
            </Container>
        )
    }

    function MainPanel(distributions) {

        return (
            <>
                <Grid gridDefinition={[{colspan: {l: 12, m: 12, default: 12}}]}>
                    <CandidateImagesTable/>
                </Grid>
                <Grid
                    gridDefinition={[
                        {colspan: {l: 6, m: 6, default: 6}},
                        {colspan: {l: 6, m: 6, default: 6}},
                    ]}
                >
                    <PreviewPanel/>
                    <ResultPanel/>
                </Grid>
            </>
        )
    }


    return (
        <CustomAppLayout
            navigation={<CustomNavi/>}
            content={<MainPanel distributions={distributions}/>}
            contentType="table"
            // stickyNotifications
        />
    );
}

function BCCLayout() {
    return (
        <App/>
    );
}

export default BCCLayout;