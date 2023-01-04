<template>
    <v-app>
    <v-container fluid>
    <p class="text-h6">Spotify APIで得られる楽曲の特徴データ(audio_features)から、ミリオンライブの楽曲を見つけるやつ</p>
    <v-spacer class="mb-4" />
    <span>指標値:</span> 
    <v-spacer class="mb-2" />
    <v-range-slider v-model="acousticness" step="0.01" min="0" max="1" label="acousticness" thumb-label="always" />
    <v-range-slider v-model="danceability" step="0.01" min="0" max="1" label="danceability" thumb-label="always" />
    <v-range-slider v-model="energy" step="0.01" min="0" max="1" label="energy" thumb-label="always" />
    <v-range-slider v-model="instrumentalness" step="0.01" min="0" max="1" label="instrumentalness" thumb-label="always" />
    <!-- <v-range-slider v-model="liveness" step="0.01" min="0" max="1" label="liveness" thumb-label="always" /> -->
    <v-range-slider v-model="loudness" step="0.01" min="-10.238" max="0" label="loudness [db]" thumb-label="always" />
    <v-range-slider v-model="mode" step="1" min="0" max="1" label="minor / major" thumb-label="always" />    
    <v-range-slider v-model="speechiness" step="0.01" min="0" max="1" label="speechiness" thumb-label="always" />
    <v-range-slider v-model="valence" step="0.01" min="0" max="1" label="valence" thumb-label="always" />

    <div class="d-flex">
        <div class="mr-2">
            <v-btn color="primary" @click="getSearchData()" width="150">指標値から探す</v-btn>
        </div>
        <div class="flex-grow-1">
            <v-btn color="primary" @click="clearSearchParam()" width="150">条件を初期化</v-btn>
        </div>
    </div>

    <v-spacer class="mb-4" />
    <div class="d-flex">
        <div class="mr-2">
            <v-btn color="primary" @click="getSearchDataFromString()" width="150">曲名から探す</v-btn>
        </div>
        <div class="flex-grow-1">
            <v-text-field v-model="search" height="10" class="caption mb-n2"
                dense clearable flat solo-inverted hide-details prepend-inner-icon="mdi-magnify"
                label="search: (曲名の一部)" @change="getSearchDataFromString()"
            />
        </div>
    </div>
    <v-spacer class="mb-4" />
    <span v-if="this.lengthResult != -1">検索結果: {{this.lengthResult}}曲（Spotify人気順に、20曲まで表示）</span>
    <template v-for="d in result" v-bind:key="d.id">
        <v-col>
            <v-card class="pa-2" elevation="10">
                <div class="d-flex">
                    <div>
                        <v-img v-bind:src="d.image" :width="this.picSize" :max-width="this.picSize" />
                    </div>
                    <div class="flex-grow-1">
                        <v-chip class="pa-2 mx-2" label>曲名</v-chip><span>{{d.name}}</span>
                    </div>
                    <div class="d-flex flex-row-reverse">
                        <v-btn icon outlined elevation="0" :href="`https://open.spotify.com/track/${d.id}?go=1`" target="_blank">
                            <v-icon>mdi-spotify</v-icon>
                        </v-btn>
                        <v-btn icon outlined elevation="0" @click="showClickDialog(d);">
                            <v-icon>mdi-tune</v-icon>
                        </v-btn>
                    </div>
                </div>
            </v-card>
        </v-col>
    </template>
    <v-spacer class="my-2" />
    <a href="https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features">
        audio_featuresに関する公式ドキュメント(developer.spotify.com)
    </a>
    <br>
    <nuxt-link to="/uma">[おまけ]Spotify APIで得られる楽曲の特徴データ(audio_features)から、ウマ娘とミリオンライブの似た曲を見つけるやつ</nuxt-link>
    <v-dialog v-model="dialog_click" max-width="400">
        <v-card>
        <v-card-text>
            この楽曲に近い指標値の楽曲を見つけられるよう、検索条件を変更します。
        </v-card-text>
        <v-card-actions class="ml-2">
            <v-btn color="gray" small @mousedown="closeClickDialog()">Cancel</v-btn>
            <v-btn small color="primary" @mousedown="searchNeighbor(); closeClickDialog();">Change</v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
    </v-container>
    </v-app>
</template>

<script>
const MIN_LOUDNESS = -10.238;
import { computed } from 'vue';
import { useDisplay } from 'vuetify';
import data from '~~/assets/json/data.json';
export default {
    setup () {
        const { name } = useDisplay()
        const picSize = computed(() => {
            switch (name.value) {
                case 'xs': return 100
                case 'sm': return 150
                case 'md': return 150
                case 'lg': return 150
                case 'xl': return 150
                case 'xxl': return 150
            }
            return undefined
        })
        return { picSize }
    },
    data () {
        return {
            dialog_click: false,
            search: '',
            buf_item: [],
            data: data.sort(function(a,b) {
                return (a.popularity > b.popularity)? -1 : 1;
            }),
            result: [],
            lengthResult: -1,
            acousticness: [0,1],
            danceability: [0,1],
            energy: [0,1],
            instrumentalness: [0,1],
            liveness: [0,1],
            loudness: [MIN_LOUDNESS,0],
            mode:[0,1],
            speechiness: [0,1],
            valence: [0,1]
        }
    },
    mounted () {
        window.addEventListener('touchend', function (event) {
            event.preventDefault();
            $(event.target).trigger('click');
        }, false);
    },
    methods: {
        getSearchData () {
            this.result = []
            this.result = this.data.filter(e => (
                this.acousticness[0] <= e.acousticness && e.acousticness <= this.acousticness[1]
                && this.danceability[0] <= e.danceability && e.danceability <= this.danceability[1]
                && this.energy[0] <= e.energy && e.energy <= this.energy[1]
                && this.instrumentalness[0] <= e.instrumentalness && e.instrumentalness <= this.instrumentalness[1]
                && this.liveness[0] <= e.liveness && e.liveness <= this.liveness[1]
                && this.loudness[0] <= e.loudness && e.loudness <= this.loudness[1]
                && this.mode[0] <= e.mode && e.mode <= this.mode[1]
                && this.speechiness[0] <= e.speechiness && e.speechiness <= this.speechiness[1]
                && this.valence[0] <= e.valence && e.valence <= this.valence[1]
                ));
            this.lengthResult = Object.keys(this.result).length
            this.result = this.result.slice(0,20)
        },
        clearSearchParam () {
            this.acousticness = [0,1]
            this.danceability = [0,1]
            this.energy = [0,1]
            this.instrumentalness = [0,1]
            // this.liveness = [0,1]
            this.loudness = [MIN_LOUDNESS,0]
            this.mode = [0,1]
            this.speechiness = [0,1]
            this.valence = [0,1]         
        },
        getSearchDataFromString () {
            this.result = []
            this.result = this.data.filter(e => e.name.toLowerCase().indexOf(this.search.toLowerCase()) != -1);
            this.lengthResult = Object.keys(this.result).length
            this.result = this.result.slice(0,20)
        },
        showClickDialog (d) {
            this.buf_item = d
            this.dialog_click = true
        },
        closeClickDialog () {
            this.dialog_click = false
        },
        searchNeighbor () {
            this.acousticness = [Math.max(0,this.buf_item.acousticness - 0.1), Math.min(1,this.buf_item.acousticness + 0.1)]
            this.danceability = [Math.max(0,this.buf_item.danceability - 0.1), Math.min(1,this.buf_item.danceability + 0.1)]
            this.energy = [Math.max(0,this.buf_item.energy - 0.1), Math.min(1,this.buf_item.energy + 0.1)]
            this.instrumentalness = [Math.max(0,this.buf_item.instrumentalness - 0.1), Math.min(1,this.buf_item.instrumentalness + 0.1)]
            // this.liveness = [0, Math.min(1,this.buf_item.liveness + 0.1)]
            this.loudness = [Math.max(MIN_LOUDNESS,this.buf_item.loudness - 1), Math.min(0,this.buf_item.loudness + 1)]
            this.mode = [this.buf_item.mode, this.buf_item.mode]
            this.speechiness = [Math.max(0,this.buf_item.speechiness - 0.1), Math.min(1,this.buf_item.speechiness + 0.1)]
            this.valence = [Math.max(0,this.buf_item.valence - 0.1), Math.min(1,this.buf_item.valence + 0.1)]
        }
    }
}
</script>

<style>
.v-label {
    min-width: 140px;
}
</style>