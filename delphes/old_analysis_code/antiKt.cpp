
    /////////////////////////////////////////
    // Manually create track jets  
    /////////////////////////////////////////

    /*******************************8
    std::cout << "Number of tracks: " << branchTrack->GetEntriesFast() << std::endl; 
    std::vector<TLorentzVector> goodTracks;
    for(Int_t i=0; i<branchTrack->GetEntriesFast(); ++i)
    {
      track = (Track*) branchTrack->At(i);
      particle = (GenParticle*) track->Particle.GetObject(); 

      if( track->PT > 1 && fabs(track->Eta) < 2.0)
      {
      
        // It is impossible for the tracker to measure the pT if it's greater than 100 GeV
        auto trackPt = track->PT;
        if (trackPt > 100){
          trackPt = 100;
        }

        if(DEBUG) plots->track_eta_phi_pt->Fill(track->Eta, track->Phi, trackPt); 
        TLorentzVector vec;
        vec.SetPtEtaPhiM( trackPt, track->Eta, track->Phi, 0.14); // pion mass in GeV 
        goodTracks.push_back(vec);
        if(DEBUG) std::cout << "Filled track vector" << std::endl;
      }
    }
    if(DEBUG) std::cout << "n tracks " << goodTracks.size() << std::endl;

    // recluster tracks into jets 
    std::vector<TLorentzVector> trackJets;
    antiKt(goodTracks, trackJets); 
    if(DEBUG) std::cout << "Found " << trackJets.size() << " jets" << std::endl;
    if(DEBUG){
      for(auto jet : trackJets){
        plots->jet_eta_phi_pt->Fill(jet.Eta(), jet.Phi(), jet.Pt());
      }
    }

    for(auto jet : trackJets) plots->allJetPt->Fill(jet.Pt());
    plots->nJets->Fill(trackJets.size());

    // nth jet plots 
    for(unsigned int i=0; i<trackJets.size() && i<7; ++i){
      plots->jetNPt.at(i)->Fill( trackJets.at(i).Pt() );
      plots->jetNEta.at(i)->Fill( trackJets.at(i).Eta() );
      plots->jetNPhi.at(i)->Fill( trackJets.at(i).Phi() );
    }
    ******************/









void antiKt(std::vector<TLorentzVector>& inputs, std::vector<TLorentzVector>& outputJets )
{
  //////////////////////////////////////////////////
  // Manual implementation of the anti-kT algorithm 
  //////////////////////////////////////////////////

  float RADIUS_PARAMETER = 0.4; 


  // anti kt algorithm 
  int nInputs = inputs.size();
  while (nInputs>0){
    Double_t dRij  = 999999999.;
    Double_t dRi   = 999999999.;
    int dRiindex   = 0;
    int dRijindex1 = 0;
    int dRijindex2 = 0;

    // Calculate the beam distance ( 1/pT_i^2 ), find the entity with the smallest beam distance  
    for (Int_t i=0; i<nInputs; ++i){
      if (pow(1./(inputs.at(i)).Pt(),2)<dRi){
        dRi      = pow(1.0/(inputs.at(i)).Pt(),2);
        dRiindex = i;
        }
    }

    // Calculate the distance metric between all entities, find the smallest distance
    for (Int_t i=0; i<nInputs-1; ++i){
      float pT_i       = inputs.at(i).Pt();
      float rapidity_i = inputs.at(i).Rapidity();
      float phi_i      = inputs.at(i).Phi();

      for (Int_t j=i+1; j<nInputs; ++j){
        float pT_j       = inputs.at(j).Pt();
        float rapidity_j = inputs.at(j).Rapidity();
        float phi_j      = inputs.at(j).Phi();

        // distance metric calculation
        //Double_t tempdRij = std::min(pow(1.0/(inputs.at(i)).Pt(),2),pow(1.0/(inputs.at(j)).Pt(),2)) * (pow((inputs.at(i)).Rapidity()-(inputs.at(j)).Rapidity(),2)+pow(acos(cos(inputs.at(i).Phi()-inputs.at(j).Phi())),2));
        float deltaRapidity = rapidity_i-rapidity_j;
        float deltaPhi = calculatDeltaPhi(phi_i, phi_j); 
        Double_t tempdRij = std::min( pT_i*pT_i, pT_j*pT_j ) * ( deltaRapidity*deltaRapidity + deltaPhi*deltaPhi ) / RADIUS_PARAMETER*RADIUS_PARAMETER;

        // find the smallest distance 
        if (tempdRij<dRij){
          dRij=tempdRij;
          dRijindex1 = i;
          dRijindex2 = j;
        }
      }
    }

    //if(DEBUG) std::cout << "smallest distance metric: " << dRij << " between: " << dRijindex1 << PrintTLorentz(inputs.at(dRijindex1)) << " and " << dRijindex2 << PrintTLorentz(inputs.at(dRijindex2)) << std::endl;

    int deleteIndex=0;
    if (dRi<dRij){ // label entity as a jet 
      deleteIndex=dRiindex;
      TLorentzVector aJet = inputs.at(dRiindex);
      outputJets.push_back( aJet ); 
    }else{ // cluster: add input entity j to entity i
      inputs.at(dRijindex1) += inputs.at(dRijindex2);
      deleteIndex=dRijindex2;
    }
    //remove the entity from the collection
    inputs.erase(inputs.begin()+deleteIndex);
    nInputs = nInputs-1;
  }
}

