
@0x9f71db4f078a6b42;
struct Schema {
	vdc @0 :Text;
	startDate @1 :Text;
	endDate @2 :Text;
	snapshotInterval @3 :Text = "2h";
	cleanupInterval @4 :Text = "1d";
	retention @5 :Text = "5d";

}
